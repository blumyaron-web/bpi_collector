import os
import json
import smtplib
import tempfile
from datetime import datetime

from typing import List, Tuple, Dict, Optional
from logging import Logger
from email.message import EmailMessage

from .report_generator import ReportGenerator
from .report_data.formatting import format_timestamp


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

    @staticmethod
    def _generate_pdf_report(samples: list, graph_path: Optional[str]) -> List[str]:
        pdf_attachments = []

        if samples:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                pdf_generator = ReportGenerator(temp_pdf.name)
                pdf_path = pdf_generator.generate_report(samples, graph_path)
                pdf_attachments = [pdf_path]

        return pdf_attachments

    def _update_email_status(
        self, samples: list, subject: str, to_address: List[str]
    ) -> None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)

        status_file = os.path.join(data_dir, "email_status.json")
        timestamp_utc = (
            samples[-1]["ts"]
            if samples and samples[-1].get("ts")
            else datetime.utcnow().isoformat() + "Z"
        )
        formatted_timestamp = format_timestamp(timestamp_utc)

        new_status = {
            "timestamp": timestamp_utc,
            "formatted_time": formatted_timestamp,
            "success": True,
            "subject": subject,
            "recipients": len(to_address),
            "sent_at": datetime.utcnow().isoformat() + "Z",
        }

        email_history = self._load_email_history(status_file)
        email_history.insert(0, new_status)
        email_history = email_history[:5]

        with open(status_file, "w") as f:
            json.dump(email_history, f)

    def _load_email_history(self, status_file: str) -> List[Dict]:

        email_history = []
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if "history" in data:
                            email_history = data["history"]
                        else:
                            old_entry = {
                                "timestamp": data.get("last_send"),
                                "success": data.get("success", False),
                                "subject": data.get("subject", "Unknown"),
                                "sent_at": data.get("last_send"),
                            }
                            if old_entry["timestamp"]:
                                email_history = [old_entry]
                    elif isinstance(data, list):
                        email_history = data
            except Exception as e:
                self.logger.warning(f"Failed to load email history: {e}")

        return email_history

    @staticmethod
    def _collect_attachments(
        pdf_attachments: List[str], graph_path: Optional[str]
    ) -> List[str]:
        all_attachments = pdf_attachments.copy()
        if graph_path and os.path.exists(graph_path):
            all_attachments.append(graph_path)
        return all_attachments

    def _cleanup_temp_files(self, pdf_attachments: List[str]) -> None:
        for pdf_file in pdf_attachments:
            try:
                os.unlink(pdf_file)
            except Exception as e:
                self.logger.warning(f"Failed to delete temporary file {pdf_file}: {e}")

    def send_report_email(
        self,
        from_address: str,
        to_address: List[str],
        subject: str,
        samples: list,
        graph_path: str = None,
    ) -> bool:
        try:
            html_generator = ReportGenerator("")
            html_content = html_generator.generate_html_report(samples)

            pdf_attachments = self._generate_pdf_report(samples, graph_path)
            self._update_email_status(samples, subject, to_address)
            all_attachments = self._collect_attachments(pdf_attachments, graph_path)

            result = self.send(
                from_address=from_address,
                to_address=to_address,
                subject=subject,
                body=html_content,
                attachments=all_attachments,
            )

            self._cleanup_temp_files(pdf_attachments)
            return result

        except Exception as e:
            error_msg = f"Failed to send report email: {str(e)}"
            self.logger.error(error_msg)
            return False

    @staticmethod
    def _create_email_message(
        subject: str, from_address: str, to_address: List[str], body: str
    ) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = ", ".join(to_address)

        plain_text = (
            body.replace("<br>", "\n").replace("<div>", "").replace("</div>", "\n")
        )
        plain_text = " ".join(plain_text.split())
        msg.set_content(plain_text)
        msg.add_alternative(body, subtype="html")

        return msg

    def _process_attachments(
        self, attachments: List[str]
    ) -> Tuple[Optional[Tuple], List[Tuple]]:
        inline_cid = None
        inline_image = None
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

        return (
            (inline_cid, inline_image) if inline_cid else (None, None)
        ), other_attachments

    @staticmethod
    def _add_attachments_to_message(
        msg: EmailMessage,
        inline_image_data: Optional[Tuple[str, Tuple]],
        other_attachments: List[Tuple],
    ) -> None:
        if inline_image_data[0]:
            inline_cid, inline_image = inline_image_data
            data, name = inline_image
            msg.add_attachment(
                data, maintype="image", subtype="png", filename=name, cid=inline_cid
            )

        for data, name, mime_type in other_attachments:
            maintype, subtype = mime_type.split("/", 1)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)

    def _send_smtp_message(self, msg: EmailMessage) -> bool:
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as s:
                s.starttls()
                s.login(self.username, self.password)
                s.send_message(msg)
            return True
        except Exception as e:
            self.logger.error(f"SMTP send failed {e}")
            return False

    def send(
        self,
        body: str,
        subject: str,
        from_address: str,
        to_address: List[str],
        attachments: List[str] = None,
    ) -> bool:
        try:
            msg = self._create_email_message(subject, from_address, to_address, body)
            inline_image_data, other_attachments = self._process_attachments(
                attachments
            )
            self.logger.info(f"Sending email {to_address}, subject={subject}")
            self._add_attachments_to_message(msg, inline_image_data, other_attachments)

            return self._send_smtp_message(msg)

        except Exception as e:
            self.logger.error(f"Failed to prepare email: {e}")
            return False
