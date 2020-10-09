# TRV Website Development (Discontinued)
This project was about creating a website for a research community that no longer exists.

The project has been shared on Github so people can learn from it, you are free to distribute, share and make changes to this code. You don't necessary need to pass the credit to me but there is nothing to stop you from doing so. 

I would love to hear from you, please let me know about tips, tricks and methodologies you think I should use; besides that if you would like to start and maintain such a community, you are free to do so.

### Features
- Sign up
- Sign in
- Blog (CRUD)
  - Create 
  - Read 
  - Update 
  - Delete
  - Rich Text editor included 
- Reset password 
- Email verification
- Invitation token
  - creation
  - verification 
- User data update
  - password
  - email
  - username 
- Uitlity functions
  - Validate email 
  - Validate username 
  - Validate password 
  - Get user's IP 
  - Generate random set of characters 
  
### Bad Practices 
- HTML code has been reused for navbar:
  - There is a solution to create a block in jinja2 with ```{% block navbar %} <nav> {% endblock %}``` and then use that whenever you want a navbar but that solution just doesn't work here.
- Too many CSS files
  - There is just too many CSS files that makes the website's design very hard to maintain, currently only I know what's going on, unfortunetly this part of the project is not easy to be used by others.
- The front-end was not designed for mobile users
  - Although it works fine or seems to work fine on iPad and similar devices.

### Vulnerabilities
This application has not been tested and I am not planning to test it but from what I can read in source code, these vulnerabilities are to be found:
- Stored XSS in blog 
- Remote command execution in thumbnail file upload for blog 
- Service side template injection
- Insecure direct object reference 

These vulnerabilities should be present because I haven't add anything to prevent them yet, you should take the code to practice:
- how flask works 
- study the features listed above 
- find these vulnerabilities and may be fix them


### How to use this project?
I have made everything very simple to use, the views.py file has everything commented out, if you are a beginner in flask, you can easily understand what's going on.

- Install dependencies by running:
```
pip3 install -r requirements.txt
```
- Run the application:
```
flask run
```

- Login credentials:
```
Email: kisho64@protonmail.com
Password: &yXxt>?sx<Zko}dk@6aX
```

### Resources used so far:
- Flask reddit community 
- pythondiscord.com 
- StackOverFlow
- Sweet Google
- Pretty Printed - YouTube channel 

## Thanks 
To everyone who was there for me, motivated me and debugged along the way.