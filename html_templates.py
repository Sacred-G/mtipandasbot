css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
width: 12%;
}
.chat-message .avatar img {
max-width: 25px;
max-height: 25px;
border-radius: 50%;
object-fit: cover;
}
.chat-message .message {
width: 90%;
padding: 0 .35rem;
color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="[Imgur](https://i.imgur.com/IO50Dybt.jpg)">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.imgur.com/6XRofYJ.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''