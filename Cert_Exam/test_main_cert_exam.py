from Cert_Exam.main_cert_exam import create_exam_cert


def test_create_exam_cert():
    create_exam_cert(can_send_email=False)
