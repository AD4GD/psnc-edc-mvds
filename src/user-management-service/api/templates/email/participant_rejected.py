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
      .rejected {
        color: #ba1a1a;
        font-size: 22px;
        margin-bottom: 14px;
      }
      .reason {
        color: #222;
        background: #ffe8e6;
        border-left: 4px solid #fa6868;
        padding: 10px 15px;
        margin-top: 22px;
        border-radius: 5px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="rejected">Registration rejected</div>
      <p>Dear {{ participant_name }},</p>
      <p>We regret to inform you that your registration was rejected by the administrator.</p>
      {% if reject_reason %}
      <div class="reason"><b>Reason:</b> {{ reject_reason }}</div>
      {% endif %}
      <p style="color:#888;margin-top:24px;font-size:13px;">If you have questions or think this is a mistake, please contact support.</p>
    </div>
  </body>
</html>
"""
