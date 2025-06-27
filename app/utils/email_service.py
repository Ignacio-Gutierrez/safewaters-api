"""
Servicio de correo electrónico para SafeWaters API.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from datetime import datetime

from app.config import settings


class EmailService:
    """Servicio para envío de correos electrónicos."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.company_name = settings.COMPANY_NAME
        
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Envía un correo electrónico."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.company_name} <{self.from_email}>"
            message["To"] = to_email
            
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            context = ssl.create_default_context()
            if getattr(settings, 'SMTP_USE_TLS', True):
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, to_email, message.as_string())
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, to_email, message.as_string())
            
            logging.info(f"Correo enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Error enviando correo a {to_email}: {e}")
            return False
    
    async def send_password_reset_email(
        self, 
        to_email: str, 
        username: str, 
        reset_token: str,
        reset_url: str
    ) -> bool:
        """Envía correo de recuperación de contraseña."""
        subject = f"Recuperar contraseña - {self.company_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #222222;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }}
                .container {{
                    width: 500px;
                    background-color: #E8DED2;
                    border: 5px solid #8B4513;
                    border-radius: 10px;
                    padding: 30px 20px;
                    margin: 30px auto;
                    color: #222222;
                }}
                .logo {{
                    font-family: Arial, sans-serif;
                    font-size: 36px;
                    font-weight: bold;
                    color: #056676;
                    margin-bottom: 0px;
                }}
                h1 {{
                    font-size: 22px;
                    color: #8B4513;
                    margin-top: 10px;
                }}
                .reset-button {{
                    display: inline-block;
                    background-color: #056676;
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .reset-button:hover {{
                    background-color: #044d5a;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                    color: #8B4513;
                }}
                .footer {{
                    margin-top: 20px;
                    color: #8B4513;
                }}
                .url-box {{
                    word-break: break-all;
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div>
                    <div class="logo">{self.company_name}</div>
                    <h1>Recuperación de Contraseña</h1>
                </div>
                
                <p style="color: #000000;">Hola <strong>{username}</strong>,</p>
                
                <p style="color: #000000;">Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
                
                <div>
                    <a href="{reset_url}" class="reset-button" stYle="color: #FFFFFF;">
                        Restablecer Contraseña
                    </a>
                </div>
                
                <div class="warning">
                    <strong>Importante:</strong>
                    <ul>
                        <li>Este enlace es válido por <strong>1 hora</strong></li>
                        <li>Si no solicitaste este cambio, ignora este correo</li>
                    </ul>
                </div>
                
                <p style="color: #000000;">Si tienes problemas con el enlace, copia y pega esta URL en tu navegador:</p>
                <p style="word-break: break-all; background: #f5f5f5; padding: 10px;">{reset_url}</p>
                
                <hr>
                <p><small>Enviado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}</small></p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Recuperación de Contraseña - {self.company_name}
        
        Hola {username},
        
        Para restablecer tu contraseña, visita: {reset_url}
        
        Este enlace es válido por 1 hora.
        Si no solicitaste este cambio, ignora este correo.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_password_changed_notification(
        self, 
        to_email: str, 
        username: str
    ) -> bool:
        """Envía una notificación de cambio de contraseña exitosa."""
        subject = f"Contraseña cambiada exitosamente - {self.company_name}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    color: #222; text-align: center; 
                }}
                .container {{ 
                    background: #E8DED2; 
                    border: 5px solid #8B4513; 
                    border-radius: 10px; 
                    padding: 30px 20px; 
                    margin: 30px auto; 
                    color: #222; 
                    max-width: 500px; 
                }}
                .logo {{ 
                    font-size: 36px; 
                    font-weight: bold; 
                    color: #056676; 
                    margin-bottom: 0px; 
                }}
                h1 {{ 
                    font-size: 22px; 
                    color: #8B4513; 
                    margin-top: 10px; 
                }}
                .footer {{ 
                    margin-top: 20px; 
                    color: #8B4513; 
                }}
            </style>
        </head>
        <body>
            <div class='container'>
                <div class='logo'>{self.company_name}</div>
                <h1>Contraseña cambiada exitosamente</h1>
                <p style="color: #000000">Hola <strong>{username}</strong>,</p>
                <p style="color: #000000">Te informamos que la contraseña de tu cuenta ha sido cambiada correctamente.</p>
                <p style="color: #000000">Si no realizaste este cambio, por favor contacta inmediatamente con nuestro soporte.</p>
                <hr>
                <p class='footer'><small>Enviado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</small></p>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Contraseña cambiada exitosamente - {self.company_name}

        Hola {username},

        Te informamos que la contraseña de tu cuenta ha sido cambiada correctamente.
        Si no realizaste este cambio, contacta con nuestro soporte.
        """
        return await self.send_email(to_email, subject, html_content, text_content)


# Instancia global
email_service = EmailService()
