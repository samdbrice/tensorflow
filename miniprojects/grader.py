from collections import namedtuple
from functools import wraps
from importlib import import_module
import json
import os
import requests
import sys
import jsonschema

from typecheck import get_validator
from static_grader import SerializedSubmission, SerializedScore, SerializedQuestion

BASE_URL = "https://www.thedataincubator.com"
HOME_DIR = os.environ["HOME"]
try:
  with open("{}/.ssh/.grader_url".format(HOME_DIR)) as submission_url_f:
    BASE_URL = submission_url_f.read().strip()
except IOError: # for local dev / general issues
  print "WARNING: You are missing a base URL. If you're developing, things will be seeded to thedataincubator.com."

try:
  # ~/.ssh is safe, hopefully
  with open("{}/.ssh/.grader_secret".format(HOME_DIR)) as secret_f:
    SECRET_GRADER_KEY = secret_f.read().strip()
except IOError: # for local dev / general issues
  print "WARNING: You are missing a unique key. Scores will still be reported, but not scored."
  print "Please show this message to a TDI staff member."
  SECRET_GRADER_KEY = 'bcgzmGuIB9yAlmshSuLy'

def is_invalid(answer, type_str):
  try:
    get_validator(type_str).validate(answer)
  except jsonschema.ValidationError as e:
    return e

  return None


def test_cases_grading(question_name, func, test_cases):
  res = []
  for test_case in test_cases:
    #test func with params in
    sub_res = func(*test_case['args'], **test_case['kwargs'])
    invalid = is_invalid(sub_res, test_case['type_str'])
    if invalid:
      print(invalid)
      return
    res.append(sub_res)

  # Submission

  submission = SerializedSubmission(question_name=question_name, submission=res)
  r = requests.post(BASE_URL + '/submission?api_key=%s' % SECRET_GRADER_KEY,
                 data={'submission': submission.dumps()})
  print "=================="
  try:
    score = SerializedScore.loads(r.text)
  except Exception as e:
    print "There was an error. Please send this output to a TDI staff member."
    print e
    print "----" * 5
    print r.text
    print "There was an error. Please send this output to a TDI staff member."
    return 

  if r.status_code != 200:
    print "Error!"
  else:
    print "Your score: ", score.score
  if score.error_msg:
    print score.error_msg
  print "=================="

def get_miniprojects():
  import glob
  current_path = os.path.dirname(os.path.realpath(__file__))
  miniprojects = [os.path.basename(n.strip("/")) for n in glob.glob(current_path + '/*/') if 'tests' not in n and 'lib' not in n]
  return miniprojects

def score(question_name, func):
  # Get test cases
  resp = requests.get(BASE_URL + '/test_cases/%s?api_key=%s' % (question_name, SECRET_GRADER_KEY))
  if resp.status_code != 200:
    print "No question found:", question_name
    return
  test_cases = json.loads(resp.text)
  test_cases_grading(question_name, func, test_cases)

# for local dev
def local_score(question_name, func):
  """
  Score locally in developer mode
  """
  # call this here because students don't have scorers
  from static_grader import scorers
  import inspect
  #reload(scorers)
  #scorers_by_name = dict(inspect.getmembers(scorers))
  scorers_by_name = scorers.DICT_SCORERS
  
  # Try to guess which project we want, based on question prefix
  miniprojects = get_miniprojects()
  prefixed_projects = [mp for mp in miniprojects if mp.lower() == question_name.split('__')[0]]
  if prefixed_projects:
    miniprojects = prefixed_projects
  all_questions = {}
  for miniproject in miniprojects:
    module = import_module(miniproject)
    reload(module)
    for question in module.questions:
      all_questions[question['name']] = question

  q = all_questions[question_name]
  test_cases = q['test_cases']
  for test_case in test_cases:
    result = func(*test_case['args'], **test_case['kwargs'])
    invalid = is_invalid(result, test_case['type_str'])
    if invalid:
      print(invalid)
      return

    answer = test_case['answer']
    Scorer = scorers_by_name[q['scorer_name']](**q['scorer_params'])
    return Scorer.score(result, answer)

client_mode = os.environ.get("GRADER_CLIENT_MODE", None)
if client_mode == "local":
  score = local_score
elif client_mode == "local_gae":
  BASE_URL = "http://localhost:8080"
