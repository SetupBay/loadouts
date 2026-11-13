FactoryBot.define do
  factory :project do
    sequence(:name) { |n| "Project #{n}" }
    status { "active" }
    owner_id { 1 }

    trait :archived do
      status { "archived" }
    end
  end
end
