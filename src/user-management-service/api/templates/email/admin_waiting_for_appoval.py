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
      .highlight {
        background: #e8f0fd;
        padding: 7px 12px;
        border-radius: 5px;
        display: inline-block;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Participant awaiting approval</h2>
      <p>The following participant has confirmed their registration and is now waiting for your review:</p>
      <p class="highlight">
        <b>Name:</b> {{ participant_name }}<br>
        <b>Email:</b> {{ participant_email }}
      </p>
      <p>Please log in to the admin panel to approve or reject the registration.</p>
    </div>
  </body>
</html>
"""
