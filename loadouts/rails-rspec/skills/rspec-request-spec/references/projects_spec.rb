require "rails_helper"

RSpec.describe "Projects API" do
  let(:owner_headers) { { "X-Owner-Id" => "1" } }
  let(:json) { response.parsed_body }

  describe "GET /projects" do
    it "lists only the current owner's projects, by name" do
      create(:project, name: "Beta")
      create(:project, name: "Alpha")
      create(:project, name: "Not mine", owner_id: 2)

      get "/projects", headers: owner_headers

      expect(response).to have_http_status(:ok)
      expect(json.pluck("name")).to eq(%w[Alpha Beta])
    end

    it "rejects a request with no owner" do
      get "/projects"

      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /projects/:id" do
    it "hides another owner's project behind a 404" do
      other = create(:project, owner_id: 2)

      get "/projects/#{other.id}", headers: owner_headers

      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /projects" do
    it "creates a project for the current owner" do
      expect {
        post "/projects", params: { project: { name: "Launch" } }, headers: owner_headers, as: :json
      }.to change(Project, :count).by(1)

      expect(response).to have_http_status(:created)
      expect(json).to include("name" => "Launch", "status" => "active", "owner_id" => 1)
    end

    it "ignores an owner_id in the body" do
      post "/projects", params: { project: { name: "Sneaky", owner_id: 2 } }, headers: owner_headers, as: :json

      expect(Project.last.owner_id).to eq(1)
    end

    it "returns 422 with errors for a duplicate name" do
      create(:project, name: "Launch")

      post "/projects", params: { project: { name: "Launch" } }, headers: owner_headers, as: :json

      expect(response).to have_http_status(:unprocessable_content)
      expect(json.dig("errors", "name")).to include("has already been taken")
    end

    # JSON bodies are wrapped under "project" by wrap_parameters, so send a form post
    # to reach params.expect with the key missing.
    it "returns 400 when the project key is missing" do
      post "/projects", params: { name: "Flat" }, headers: owner_headers

      expect(response).to have_http_status(:bad_request)
    end
  end

  describe "PATCH /projects/:id" do
    it "archives a project" do
      project = create(:project)

      patch "/projects/#{project.id}", params: { project: { status: "archived" } }, headers: owner_headers, as: :json

      expect(response).to have_http_status(:ok)
      expect(project.reload.status).to eq("archived")
    end

    it "rejects an unknown status" do
      project = create(:project)

      patch "/projects/#{project.id}", params: { project: { status: "deleted" } }, headers: owner_headers, as: :json

      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "DELETE /projects/:id" do
    it "deletes the owner's project" do
      project = create(:project)

      expect { delete "/projects/#{project.id}", headers: owner_headers }.to change(Project, :count).by(-1)
      expect(response).to have_http_status(:no_content)
    end
  end
end
