#!/bin/bash

gunicorn src.main:app --bind=0.0.0.0:8000
