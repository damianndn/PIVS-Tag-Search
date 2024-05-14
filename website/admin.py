from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from sqlalchemy.inspection import inspect

admin = Blueprint('admin',__name__)


