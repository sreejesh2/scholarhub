import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_otp_email(otp, recipient_email):
    # SMTP credentials
    smtp_server = 'email-smtp.ap-south-1.amazonaws.com'
    smtp_port = 587  # or 25 or 465 (for SSL)
    smtp_username = 'AKIA2SY2WDVB4SQLA36A'
    smtp_password = 'BKNJ6xKeCmnPn+RhwpKiKHk0rAR3Ms5kU/9HGUhIstky'

    # Sender and recipient information
    sender_email = 'Luminar Technolab <info@luminartechnohub.com>'

    # Email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'OTP'
    
    # HTML content with placeholders for OTP
    media_query = """
    @media only screen and (max-width: 600px) {
      .container {
        width: 100% !important;
      }
    }
    """
    
    email_content = """\
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Scholar Hub</title>
    <style>
       {media_query}
      </style>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
    
      <table class="container" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; border-collapse: collapse;">
        <tr>
          <td style="background-color: #f5f5f5; padding: 20px; text-align: center;">
            <div style="display: flex; align-items: center;">
                <h1 style="margin: 0;">Scholar Hub</h1>
            </div>
          </td>
        </tr>
        <tr>
          <td style="background-color: #ffffff; padding: 20px;">
            <h5 style="margin-top: 0;">Your OTP is <span style="font-size: 18px;">{fa_otp}</span> for verification purposes. Do not share OTP for security reasons</h5>
            <p style="margin-bottom: 0;">Best regards,<br>Luminar Technolab Team</p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """.format(fa_otp=otp, media_query=media_query)

    message.attach(MIMEText(email_content, 'html'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

        # Close the connection
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



