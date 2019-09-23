from fastapi import FastAPI, Path, Query, File, UploadFile, Form
from typing import List

from starlette.responses import HTMLResponse
from pydantic import BaseModel

from vn.vn import VisualNarrator


vn_app = FastAPI()
vn = VisualNarrator()


class UserStoryFile(BaseModel):
    file_name: str
    system_name: str
    success: str
    output: dict


@vn_app.get('/')
def root():
    content = '''<title>VisualNarrator API entry point</title>
    <style>
        form { background-color: #ededed; padding: 7px; font-family: sans-serif }
        form h1 { font-size: 16px }
        p { background-color: #fbfbfb; padding: 3px 4px; margin: 6px 0px; font-size: 12px }
    </style>
    <body>
    <form action="/mineform/" enctype="multipart/form-data" method="post">
    <h1>Visual Narrator</h1>
    <p>User story file:<br>
    <input name="file" type="file"></p>
    <p>System name:<br>
    <input name="systemname" type="text" value="System"></p>
    <p>Optional outputs to include:<br>
    <input id="prolog" name="prolog" type="checkbox">Prolog<br>
    <input id="json" name="json" type="checkbox">JSON<br>
    <input id="report" name="report" type="checkbox">HTML Report</p>
    <input type="submit" value="Run Visual Narrator">
    </form>
    </body>
    '''
    return HTMLResponse(content=content)


def __stories_from_file(lines: List[str]):
    return [str(line).lstrip('b\'').rstrip('\\n\'') for line in lines]


def __mine(file_name: str,
           stories: List[str],
           systemname: str,
           prolog: bool = False,
           json: bool = False,
           report: bool = False):
    success = False

    # Read file contents
    if stories:
        success = True

    # Pass settings
    vn.prolog = prolog
    vn.json = json

    # Run VN
    res = vn.run(file_name,
                 systemname,
                 stories=stories,
                 write_local=False)

    # Fill output
    output = {}
    output['ontology'] = res['output_ontobj']

    if prolog:
        output['prolog'] = res['output_prologobj']
    if json:
        output['json'] = res['output_json']
    if report:
        output['report'] = res['report']

    return {"file_name": file_name,
            "system_name": systemname,
            "success": success,
            "output": output}


@vn_app.post("/mine/", response_model=UserStoryFile)
async def mine_user_stories(file: UploadFile = File(...),
                            systemname: str = Query('System', description='Name of system', min_length=1),
                            prolog: bool = Query(False, description='Return Prolog'),
                            json: bool = Query(False, description='Return JSON'),
                            report: bool = Query(False, description='Return HTML report')):
    stories = __stories_from_file(file.file.readlines())
    return __mine(file_name=file.filename,
                  systemname=systemname,
                  stories=stories,
                  prolog=prolog,
                  json=json,
                  report=report)


@vn_app.post("/mineform/", response_model=UserStoryFile)
async def mine_user_stories_form(file: UploadFile = File(...),
                                 systemname: str = Form('System', min_length=1),
                                 prolog: bool = Form(False),
                                 json: bool = File(False),
                                 report: bool = File(False)):
    stories = __stories_from_file(file.file.readlines())
    return __mine(file_name=file.filename,
                  systemname=systemname,
                  stories=stories,
                  prolog=prolog,
                  json=json,
                  report=report)
