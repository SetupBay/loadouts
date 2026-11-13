require "test_helper"

class OrderTest < ActiveSupport::TestCase
  setup do
    @customer = Customer.create!(email: "  Ada@Example.com ")
  end

  test "normalises customer email" do
    assert_equal "ada@example.com", @customer.email
  end

  test "requires a well-formed, unique reference" do
    Order.create!(customer: @customer, reference: "ORD-000001", total_pence: 1250)
    duplicate = Order.new(customer: @customer, reference: "ORD-000001")
    assert_not duplicate.valid?
    assert_includes duplicate.errors[:reference], "has already been taken"
    assert_not Order.new(customer: @customer, reference: "123").valid?
  end

  test "rejects negative totals and unknown statuses" do
    order = Order.new(customer: @customer, reference: "ORD-000002", total_pence: -1, status: "lost")
    assert_not order.valid?
    assert order.errors.key?(:total_pence)
    assert order.errors.key?(:status)
  end

  test "formats the total in pounds" do
    assert_equal "£12.50", Order.new(total_pence: 1250).total
  end

  test "paid scope filters by status" do
    paid = Order.create!(customer: @customer, reference: "ORD-000003", status: "paid")
    Order.create!(customer: @customer, reference: "ORD-000004")
    assert_equal [ paid ], Order.paid.to_a
  end

  test "with_customer avoids N+1 queries" do
    3.times { |i| Order.create!(customer: Customer.create!(email: "c#{i}@example.com"), reference: format("ORD-1%05d", i)) }
    assert_queries_count(2) do
      Order.with_customer.each { |order| order.customer.email }
    end
  end
end
