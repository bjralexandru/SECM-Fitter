​
<h1>SECM Approach Curve Fitter</h1>
<h3> A one-stop solution for all your Scanning Electrochemical Microscopy approach curve experiments</h3>

[![Made with - Python](https://img.shields.io/badge/Made_with-Python-2ea44f?style=for-the-badge&logo=Python&logoColor=black)](https://www.python.org/)  [![Made with - Chart.js](https://img.shields.io/badge/Made_with-Chart.js-purple?style=for-the-badge&logo=Chart.js&logoColor=black)](https://www.chartjs.org/)
[![Made with - Flask](https://img.shields.io/badge/Made_with-Flask-blue?style=for-the-badge&logo=Flask&logoColor=black)](https://flask.palletsprojects.com/en/2.2.x/) [![Build - Live](https://img.shields.io/badge/Build-Live-2ea44f?style=for-the-badge&logo=Live&logoColor=Green)](https://secmfitter-production-3804.up.railway.app)


[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 

### [NEW!] Project is now live at [https://secmfitter-production-3804.up.railway.app](https://secmfitter-production-3804.up.railway.app).

With this project, I intended to build a tool that we can use within our lab for the experiments concerning the approach curves obtained with the Scanning Electrochemical Microscopy instrumentation.

<h3> What was the problem? </h3>

In a classical workflow, I'd extract the data from the acquisition software of the equipment, bring it to my workstation and perform some cleaning before attempting to perform a non-linear least-square fitting on it. The problem resides in the fact that I'd end up with a bunch of excel files for each series of approach curves, which made going over past experiments pretty tedious and relies on my capacity to stay organized.

<h3> How is this application addressing the shortcoming? </h3>

First, it is a user-based web application, so anyone who wishes to sign up gets a private space where he/she can upload his/her data, fit the approach curves one at a time, extract the parameters of interest and also get a graphical representation of the goodness of fit.


<img src='https://user-images.githubusercontent.com/44103446/206875675-4172e749-3864-448b-9f8c-d9ba52f622b3.png' width=450 height=300/> <img src='https://user-images.githubusercontent.com/44103446/206875810-33785d68-dedd-4e71-b1ee-103a5ef4e044.png' width=450 height=300/>

Data should be formatted such that it has 3 columns without headers: first for the index, second for the distance (in microns), and third for the current (in nA). After uploading the .xls or .csv file the user provides the values for the parameters used in his/her particular experiment and fits his/her dataset.

<img src="https://user-images.githubusercontent.com/44103446/206876828-9cfb27e9-4263-45ff-b34a-8e6ab396dd53.png" widht=450 height=300/> <img src='https://user-images.githubusercontent.com/44103446/206876856-56c4893e-7e12-40e9-a11a-b19765c379e0.png' width=450 height=300 />



Moreover, when someone wishes to go over past results or verify something, he/she can go to the 'Query Data' tab and scroll through all his/her past experiments.

<img src='https://user-images.githubusercontent.com/44103446/206875858-02fa9b5d-92fa-4dc1-bcc8-faab876a145e.png' width=450 height=300/> <img src='https://user-images.githubusercontent.com/44103446/206875923-edeacad8-f9de-418c-89af-f00ba94f6005.png' width=450 height=300/>





The function used for the generation of the theoretical current values comes from an [article](https://doi.org/10.1016/j.jelechem.2007.09.021) written by R.Cornut and C.Lefrou.

As of now, it uses a basic SQLite database for the user's information and the .xls/.csv files are saved locally. I'm currently searching for solutions to put it live either on Heroku or Railway and I'll switch to PostgreSQL for the user's info and maybe a blob storage or bucket for the files.

<h3> Help and feedback are very much appreciated! </h3>


