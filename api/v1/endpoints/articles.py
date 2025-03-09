from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.article import ArticleResponse, ArticleCreate

router = APIRouter(prefix='/articles', tags=['articles'])

articles = []


def add_article(article: ArticleCreate):
    articles.append(article)
    print(articles)


@router.post('/')
async def create_article(article: ArticleCreate):
    add_article(article)
    return articles


@router.get('/')
async def show_article():
    return articles
