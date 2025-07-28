from flask import current_app
from flask_mail import Message
from threading import Thread
import logging

def send_async_email(app, msg):
    """Envia email em segundo plano"""
    with app.app_context():
        try:
            from app import mail
            mail.send(msg)
            current_app.logger.info(f"Email enviado com sucesso para {msg.recipients}")
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")

def send_confirmation_email(employee_name, date, points, refinery, observations):
    """Envia email de confirmação quando um ponto é registrado"""
    # Mapeamento de funcionários para emails
    recipient = {
        'Rodrigo': 'rodrigo@monitorarconsultoria.com.br',
        'Maurício': 'carlos.mauricio.prestserv@petrobras.com.br',
        'Matheus': 'Matheus.e.lima.prestserv@petrobras.com.br',
        'Wesley': 'Wesley_fgc@hotmail.com'
    }.get(employee_name)
    
    if recipient:
        try:
            from app import mail
            msg = Message(
                subject="Confirmação de Ponto Registrado",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[recipient],
                cc=[current_app.config['MAIL_USERNAME']]
            )
            msg.body = f"""
            Olá {employee_name},
            
            Seu ponto foi registrado com sucesso:
            
            Data/Hora: {date}
            Refinaria: {refinery}
            Pontos: {points}
            Observações: {observations}
            
            Atenciosamente,
            Sistema de Pontos
            """
            
            # Enviar email em segundo plano
            Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
            current_app.logger.info(f"Email de confirmação enviado para {employee_name}")
            
        except Exception as e:
            current_app.logger.error(f"Erro ao preparar email para {employee_name}: {str(e)}")
    else:
        current_app.logger.warning(f"Email não encontrado para funcionário: {employee_name}") 