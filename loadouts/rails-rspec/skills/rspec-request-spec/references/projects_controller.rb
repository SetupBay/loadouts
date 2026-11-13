# JSON API for projects, scoped to the current owner. In a real app the owner
# comes from authentication; here it is a header so the specs can show the scoping.
class ProjectsController < ApplicationController
  before_action :require_owner
  before_action :set_project, only: %i[show update destroy]

  def index
    render json: Project.owned_by(@owner_id).order(:name).limit(100)
  end

  def show
    render json: @project
  end

  def create
    project = Project.new(project_params.merge(owner_id: @owner_id))
    if project.save
      render json: project, status: :created, location: project
    else
      render json: { errors: project.errors }, status: :unprocessable_content
    end
  end

  def update
    if @project.update(project_params)
      render json: @project
    else
      render json: { errors: @project.errors }, status: :unprocessable_content
    end
  end

  def destroy
    @project.destroy!
    head :no_content
  end

  private
    def require_owner
      @owner_id = Integer(request.headers.fetch("X-Owner-Id"))
    rescue KeyError, ArgumentError
      head :unauthorized
    end

    # Another owner's project is a 404, not a 403: do not confirm that it exists.
    def set_project
      @project = Project.owned_by(@owner_id).find_by(id: params[:id])
      head :not_found unless @project
    end

    def project_params
      params.expect(project: %i[name status])
    end
end
