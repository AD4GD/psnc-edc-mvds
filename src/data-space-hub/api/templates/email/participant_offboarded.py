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
      .title { color: #c0392b; font-size: 22px; margin-bottom: 14px; }
      .info-box {
        background: #fff5f5;
        border: 1px solid #f5c6cb;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 18px 0;
        font-size: 14px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">Offboarded from Data Space</div>
      <p>Dear {{ participant_name }},</p>
      {% if initiated_by == "admin" %}
      <p>Your organization has been <strong>offboarded from the Data Space</strong> by an administrator.</p>
      {% else %}
      <p>Your offboarding request has been processed. Your organization has been <strong>removed from the Data Space</strong>.</p>
      {% endif %}
      <div class="info-box">
        <strong>What this means:</strong><br>
        • Your participant record and credentials have been removed.<br>
        • Your login access to the portal has been revoked.<br>
        • Any active connectors will no longer be recognized by the Data Space.
      </div>
      {% if reason %}
      <p><strong>Reason:</strong> {{ reason }}</p>
      {% endif %}
      <p style="color:#888; margin-top:24px; font-size:13px;">
        If you believe this was done in error or have any questions, please contact the Data Space administrator.
      </p>
    </div>
  </body>
</html>
"""
