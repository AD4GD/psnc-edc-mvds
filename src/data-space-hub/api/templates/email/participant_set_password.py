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
      .title {
        color: #1a73e8;
        font-size: 22px;
        margin-bottom: 14px;
      }
      .credentials-box {
        background: #f0f4ff;
        border: 1px solid #c8d6f0;
        border-radius: 6px;
        padding: 16px 20px;
        margin: 18px 0;
      }
      .credentials-box p { margin: 4px 0; }
      .credentials-box .label { color: #555; font-size: 13px; }
      .credentials-box .value { font-weight: bold; font-size: 15px; color: #111; }
      .btn {
        display: inline-block;
        background: #1a73e8;
        color: #fff;
        padding: 12px 28px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 12px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">Welcome to the Data Space!</div>
      <p>Dear {{ participant_name }},</p>
      <p>Your registration has been approved and your account has been created.</p>
      <p>Please log in using the temporary credentials below. You will be asked to set a new password on your first login.</p>

      <div class="credentials-box">
        <p><span class="label">Portal URL:</span></p>
        <p><span class="value">{{ portal_url }}</span></p>
        <p><span class="label">Username (email):</span></p>
        <p><span class="value">{{ email }}</span></p>
        <p><span class="label">Temporary password:</span></p>
        <p><span class="value">{{ temporary_password }}</span></p>
      </div>

      <p><a href="{{ portal_url }}" class="btn">Log in to the Portal</a></p>

      <p style="color:#c00;margin-top:18px;font-size:13px;">⚠️ Please change your password immediately after logging in.</p>
      <p style="color:#888;margin-top:12px;font-size:13px;">If you have any questions, just reply to this email.</p>
    </div>
  </body>
</html>
"""
