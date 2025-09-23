import os
import json
import smtplib
import tempfile
from typing import List
from logging import Logger
from email.message import EmailMessage

from .report_generator import ReportGenerator


class EmailSender:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        logger: Logger,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logger

    def send_report_email(
        self,
        from_address: str,
        to_address: List[str],
        subject: str,
        samples: list,
        graph_path: str = None,
    ) -> bool:
        try:
            graph_path: str
            pdf_attachments = []

            html_generator = ReportGenerator("")
            html_content = html_generator.generate_html_report(samples)

            if samples:
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False
                ) as temp_pdf:
                    pdf_generator = ReportGenerator(temp_pdf.name)
                    pdf_path = pdf_generator.generate_report(samples, graph_path)
                    pdf_attachments = [pdf_path]

            # Record email status
            status_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "email_status.json"
            )
            email_status = {
                "last_send": samples[-1]["ts"] if samples else None,
                "success": True,
                "subject": subject,
            }
            with open(status_file, "w") as f:
                json.dump(email_status, f)

            all_attachments = pdf_attachments.copy()
            if os.path.exists(graph_path):
                all_attachments.append(graph_path)

            result = self.send(
                from_address=from_address,
                to_address=to_address,
                subject=subject,
                body=html_content,
                attachments=all_attachments,
            )

            for pdf_file in pdf_attachments:
                try:
                    os.unlink(pdf_file)
                except Exception as e:
                    self.logger.warning(e)

            return result

        except Exception as e:
            error_msg = f"Failed to send report email: {str(e)}"
            self.logger.error(error_msg)
            return False

    def send(
        self,
        body: str,
        subject: str,
        from_address: str,
        to_address: List[str],
        attachments: List[str] = None,
    ) -> bool:

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = ", ".join(to_address)

        plain_text = (
            body.replace("<br>", "\n").replace("<div>", "").replace("</div>", "\n")
        )

        plain_text = " ".join(plain_text.split())
        msg.set_content(plain_text)

        inline_cid = None
        other_attachments = []

        for path in attachments or []:
            if not os.path.exists(path):
                continue

            try:
                with open(path, "rb") as f:
                    data = f.read()
                if path.lower().endswith(".png") and not inline_cid:
                    inline_cid = "graphimage"
                    inline_image = (data, os.path.basename(path))
                elif path.lower().endswith(".pdf"):
                    other_attachments.append(
                        (data, os.path.basename(path), "application/pdf")
                    )
                else:
                    other_attachments.append(
                        (data, os.path.basename(path), "application/octet-stream")
                    )

            except Exception as e:
                self.logger.error(f"Failed to read attachment {path}\n{e}")

        self.logger.info(f"Sending email {to_address}, subject={subject}")

        try:
            msg.add_alternative(body, subtype="html")
            if inline_cid and "inline_image" in locals():
                data, name = inline_image
                msg.add_attachment(
                    data, maintype="image", subtype="png", filename=name, cid=inline_cid
                )

            for data, name, mime_type in other_attachments:
                maintype, subtype = mime_type.split("/", 1)
                msg.add_attachment(
                    data, maintype=maintype, subtype=subtype, filename=name
                )

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as s:
                s.starttls()
                s.login(self.username, self.password)
                s.send_message(msg)

            return True

        except Exception as e:
            self.logger.error(f"SMTP send failed {e}")
            return False
