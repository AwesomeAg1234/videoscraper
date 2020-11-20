from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import flask
from flask import Flask
from threading import Thread
import json
import os
import time

def _init_bin(executable_name):
    start = time.clock()
    if not os.path.exists(BIN_DIR):
        print("Creating bin folder")
        os.makedirs(BIN_DIR)
    print("Copying binaries for " + executable_name + " in /tmp/bin")
    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)
    shutil.copy2(currfile, newfile)
    print("Giving new binaries permissions for lambda")
    os.chmod(newfile, 0o775)
    elapsed = time.clock() - start
    print(executable_name + " ready in " + str(elapsed) + "s.")
def video(url):
  _init_bin("chromedriver")
  chrome_options = Options()
  chrome_options.add_argument("--no-sandbox")


  with Chrome(options=chrome_options,executable_path="chromedriver") as browser:
       browser.get(url)
       html = browser.page_source

  page_soup = BeautifulSoup(html, 'html.parser')
  containers = page_soup.findAll("video")#,{"class":"grid-item"})
  #print(containers)
  con = str(containers)
  con = con.replace(" ",",")
  con = con.split(",")
  #print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
  print(con)
  vidlink = con[len(con)-2]
  vidlink = vidlink.replace("src=\"","")
  vidlink = vidlink.replace('"',"")
  vidlink = vidlink.replace('&amp;',"&")
  #print(vidlink)
  return vidlink
def check(url):
  with open("videos.json",mode="r") as v:
    vid = json.load(v)
    vurl = vid[url]["vurl"]
    vtime = vurl.split("&t=")[1]
    current = time.time()
    dif = current - int(vtime)
    if dif > 599:
      return True
    else:
      return False
def addurl(url):
  with open("videos.json",mode="r") as v:

    vid = json.load(v)
    vurl = video(url)
    try:
      vid[url]["vurl"] = vurl
    except KeyError:
      dict_value = {url:{"vurl":vurl}}
      vid.update(dict_value)
  with open("videos.json",mode="w") as v:
    json.dump(vid, v)




def getit(url):
  with open("videos.json",mode="r") as v:
    print(url)
    vid = json.load(v)
    if url in vid:

      if check(url):
        return url
      else:
        return video(url)
    else:
      addurl(url)
      return video(url)

app = Flask('')
@app.route('/')
def main():
    return "NO"
def run():
    app.run(host="0.0.0.0", port=80)
def keep_alive():
    server = Thread(target=run)
    server.start()
keep_alive()
@app.route('/get', methods=['GET'])
def getlink():
  url = flask.request.args.get('url')
  url = getit(url)
  return f"""<meta http-equiv="refresh" content="0; URL={url}" />"""
