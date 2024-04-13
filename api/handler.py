from flask import Flask, Request
from .ParallelRun import app

def handler(event, context):
    return app(event, context)