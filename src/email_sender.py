import os
import logging
import win32com.client as win32


class EmailSender:

    @staticmethod
    def enviar(
        destinatarios,
        assunto,
        mensagem,
        anexo=None
    ):

        try:

            outlook = win32.Dispatch(
                "Outlook.Application"
            )

            email = outlook.CreateItem(0)

            if isinstance(
                destinatarios,
                list
            ):

                destinatarios = ";".join(
                    destinatarios
                )

            email.To = destinatarios

            email.Subject = assunto

            email.HTMLBody = mensagem

            if anexo:

                if os.path.exists(anexo):

                    email.Attachments.Add(
                        os.path.abspath(anexo)
                    )

                else:

                    logging.warning(
                        f"Anexo não encontrado: "
                        f"{anexo}"
                    )

            email.Send()

            logging.info(
                f"""
                EMAIL ENVIADO

                Destinatários:
                {destinatarios}

                Assunto:
                {assunto}

                Anexo:
                {anexo}
                """
            )

            return True

        except Exception as erro:

            logging.exception(
                "ERRO AO ENVIAR E-MAIL"
            )

            raise Exception(
                f"Falha ao enviar e-mail: {erro}"
            )