# Frequently Asked Questions
### How can I test content before submitting a pull request?
If you have forked the repository, you need to install and run the IoT Atlas in a local copy of Hugo. You can do that through the following steps.
1. In the local forked repository execute: `git submodule update --init --recursive` which will pull in the necessary Hugo templates.
1. Install Hugo following [these instructions](https://gohugo.io/getting-started/installing/).
1. Start a local Hugo server: `hugo server --buildDrafts -v` which will build all pages, if they are in a draft state or not.    
  **Note**: you should see a message such as `Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
` when the Hugo server is operating correctly.   
1. Browse to the local Hugo server. 
