class Project < ApplicationRecord
  STATUSES = %w[active archived].freeze

  validates :name, presence: true, length: { maximum: 80 }, uniqueness: { scope: :owner_id }
  validates :status, inclusion: { in: STATUSES }
  validates :owner_id, presence: true

  scope :owned_by, ->(owner_id) { where(owner_id: owner_id) }
end
