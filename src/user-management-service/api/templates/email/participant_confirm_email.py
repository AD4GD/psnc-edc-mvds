TEMPLATE = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; color: #222; background: #f8f8f8; }
      .container {
        background: #fff;
        margin: 40px auto;
        padding: 32px 36px;
        max-width: 500px;
        border-radius: 8px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.09);
      }
      .btn {
        background: #346bea;
        color: #fff!important;
        padding: 14px 24px;
        font-size: 18px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin-top: 18px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Hello {{ participant_name }},</h2>
      <p>Thank you for registering as a participant in our platform!</p>
      <p>To complete your registration, please confirm your email address by clicking the link below:</p>
      <a href="{{ confirmation_link }}" class="btn">Confirm your email</a>
      <p style="color:#888;margin-top:24px;font-size:13px;">If you did not initiate this registration, simply ignore this message.</p>
    </div>
  </body>
</html>

"""
