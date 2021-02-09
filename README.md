# SimpleForum
![](etc/home/home.jpg)
Simple General Forum is made using Flask, Bootstrap, HTML, Javascript      
This forum page have basic CRUD functions   
member register or login and write new a post, read, update, delete the post 

# Templates Preview
### This Pages are optimized for Chrome, Edge browser   

- ### Register
        Register process : Agree -> User input -> Finish

<center>
    <img src="etc/register/agree.jpg" width="300" height="300">
    <img src="etc/register/form.jpg" width="300" height="300">
    <img src="etc/register/finish.jpg" width="600">
</center>
<br/>

<center>
    <h3>Register create page have tooltips for notifying each input's rules</h3>
    <img src="etc/register/tooltip.jpg">
</center>
<hr/>

- ### Home
        In homepage, You can login and logout, or read posts.
<center>
    <img src="etc/home/login.jpg">
    <h3>if you login success ↓</h3>
    <img src="etc/home/login_ok.jpg">
</center>

<hr/>

- ### Boards
<center>
    <img src="etc/board/list.jpg">
    <img src="etc/board/view.jpg">
    <img src="etc/board/detail_view.jpg">
    <img src="etc/board/write.jpg">
</center>


# Security
- To prevent CSRF attack, apply CSRF Protect.
- To prohibit direct access, apply RegisterToken in Register agree step.

# Database
- Class Diagram
<center>
    <img src="etc/board/diagram.jpg">
    <p>Use MySQL and SQLAlchemy</p>
</center>

# Requirement
Check requirements.txt   

    bcrypt==3.2.0       
    cffi==1.14.4    
    click==7.1.2    
    Flask==1.1.2    
    Flask-Bcrypt==0.7.1
    Flask-SQLAlchemy==2.4.4
    Flask-WTF==0.14.3
    itsdangerous==1.1.0
    Jinja2==2.11.2
    MarkupSafe==1.1.1
    mysqlclient==2.0.3
    pycparser==2.20
    pycryptodomex==3.9.9
    PyMySQL==1.0.2
    six==1.15.0
    SQLAlchemy==1.3.22
    Werkzeug==1.0.1
    WTForms==2.3.3

# License
MIT License
