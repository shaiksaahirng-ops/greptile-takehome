from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/api/changelogs", tags=["changelogs"])

@router.get("", response_model=List[schemas.ChangelogResponse])
def get_changelogs(
    skip: int = 0, 
    limit: int = 50,
    project: str = None,
    db: Session = Depends(get_db)
):
    """Get all published changelogs, ordered by creation date (newest first)"""
    query = db.query(models.Changelog).filter(models.Changelog.published == True)
    if project:
        query = query.filter(models.Changelog.project_name == project)
    return query.order_by(models.Changelog.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{changelog_id}", response_model=schemas.ChangelogResponse)
def get_changelog(changelog_id: int, db: Session = Depends(get_db)):
    """Get a specific changelog by ID"""
    changelog = db.query(models.Changelog).filter(models.Changelog.id == changelog_id).first()
    if not changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")
    return changelog

@router.post("", response_model=schemas.ChangelogResponse, status_code=201)
def create_changelog(changelog: schemas.ChangelogCreate, db: Session = Depends(get_db)):
    """Create a new changelog entry"""
    db_changelog = models.Changelog(
        version=changelog.version,
        title=changelog.title,
        summary=changelog.summary,
        changes=changelog.changes.model_dump(),
        commit_range=changelog.commit_range,
        project_name=changelog.project_name,
        published=True
    )
    db.add(db_changelog)
    db.commit()
    db.refresh(db_changelog)
    return db_changelog

@router.put("/{changelog_id}", response_model=schemas.ChangelogResponse)
def update_changelog(
    changelog_id: int, 
    changelog: schemas.ChangelogUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing changelog"""
    db_changelog = db.query(models.Changelog).filter(models.Changelog.id == changelog_id).first()
    if not db_changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")
    
    update_data = changelog.model_dump(exclude_unset=True)
    if "changes" in update_data and update_data["changes"]:
        update_data["changes"] = update_data["changes"]
    
    for key, value in update_data.items():
        setattr(db_changelog, key, value)
    
    db.commit()
    db.refresh(db_changelog)
    return db_changelog

@router.delete("/{changelog_id}", status_code=204)
def delete_changelog(changelog_id: int, db: Session = Depends(get_db)):
    """Delete a changelog"""
    db_changelog = db.query(models.Changelog).filter(models.Changelog.id == changelog_id).first()
    if not db_changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")
    db.delete(db_changelog)
    db.commit()
    return None
