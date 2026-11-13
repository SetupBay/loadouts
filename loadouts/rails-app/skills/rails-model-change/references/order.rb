class Customer < ApplicationRecord
  has_many :orders, dependent: :restrict_with_error

  normalizes :email, with: ->(email) { email.strip.downcase }
  validates :email, presence: true, uniqueness: true
end

class Order < ApplicationRecord
  STATUSES = %w[pending paid refunded].freeze

  belongs_to :customer

  validates :reference, presence: true, uniqueness: true, format: { with: /\AORD-\d{6}\z/ }
  validates :total_pence, numericality: { only_integer: true, greater_than_or_equal_to: 0 }
  validates :status, inclusion: { in: STATUSES }

  scope :paid, -> { where(status: "paid") }
  scope :with_customer, -> { includes(:customer) }

  def total
    format("£%.2f", total_pence / 100.0)
  end
end
