import { Button, Card, Form, Input, notification } from "antd";
import { useForm } from "antd/es/form/Form";
import { useNavigate } from "react-router-dom";
import "../style/login.css"

export const LoginPage = () => {
  const [form] = useForm();
  const navigate = useNavigate();

  const formSubmit = () => {
    if (form.getFieldValue("username") !== "q4usAdmin" || form.getFieldValue("password") !== "Cvq4PWD#1"){
      notification.error({message: "Username or Password is incorrect!", duration: 2})
    }
    else {
      navigate("/jobs")
    }
  }
  
	return (
		<div className={"login-container"}>
        <Card className={"card-style"}>
          <div className={"login-content"}>
              <div className={"header-content"}>
                  <img className={"image-style"} src={"/logo.png"}/>
              </div>
              <div>
                  <Form
                      name="basic"
                      form={form}
                      onFinish={formSubmit}
                  >
                      <Form.Item
                          label={<div className={"login-label-style"}>Username</div>}name="username"
                          rules={[{ required: true, message: "Please enter your username!" }]}
                      >
                          <Input
                              className={"input-style"}
                              autoComplete="off"
                          />
                      </Form.Item>
                      <Form.Item
                          label={<div className={"login-label-style"}>Password</div>}
                          name="password"
                          rules={[{ required: true, message: "Please enter your password!" }]}
                      >
                          <Input.Password
                              className={"input-style"}
                              autoComplete="off"
                          />
                      </Form.Item>
                      <Form.Item>
                          <Button
                              className={"btn-style"}
                              type={"primary"}
                              htmlType={"submit"}
                          >
                              <div className={"btn-label"}>Sign In</div>
                          </Button>
                      </Form.Item>
                  </Form>
              </div>
          </div>
        </Card>
    </div>
	);
};
