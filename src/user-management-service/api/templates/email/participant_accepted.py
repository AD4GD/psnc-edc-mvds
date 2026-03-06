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
      .success {
        color: #25a244;
        font-size: 22px;
        margin-bottom: 14px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="success">Registration approved!</div>
      <p>Dear {{ participant_name }},</p>
      <p>Your registration has been reviewed and approved by an administrator.</p>
      <p>Your infrastructure has now full possibilities and connection with whole Data Space. Welcome aboard!</p>
      <p style="color:#888;margin-top:24px;font-size:13px;">If you have any questions, just reply to this email.</p>
    </div>
  </body>
</html>
"""
