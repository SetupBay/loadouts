class CreateOrders < ActiveRecord::Migration[8.1]
  def change
    create_table :customers do |t|
      t.string :email, null: false
      t.timestamps
    end
    add_index :customers, :email, unique: true

    create_table :orders do |t|
      t.references :customer, null: false, foreign_key: true
      t.string :reference, null: false
      t.integer :total_pence, null: false, default: 0
      t.string :status, null: false, default: "pending"
      t.timestamps
    end
    add_index :orders, :reference, unique: true
  end
end
