from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import ResearchProject, User
from ..services.paper_upload_service import save_uploaded_pdf


router = APIRouter(
    prefix="/projects",
    tags=["Paper Full Text"]
)


@router.post(
    "/{project_id}/papers/{paper_id}/upload-pdf"
)
def upload_paper_pdf(
    project_id: int,
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        project = (
            db.query(ResearchProject)
            .filter(
                ResearchProject.id == project_id,
                ResearchProject.user_id == current_user.id,
            )
            .first()
        )
        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        result = save_uploaded_pdf(
            db=db,
            project_id=project_id,
            paper_id=paper_id,
            file=file
        )

        return {
            "message": "PDF uploaded and processed successfully",
            "result": result
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )