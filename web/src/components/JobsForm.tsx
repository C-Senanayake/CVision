import React from "react";
import { Button, Form, Input, Flex, Select, Upload, InputNumber } from "antd";
import { addJob } from "../api";
import type { FormProps } from 'antd';
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import ReactQuill , { Quill } from "react-quill-new";
import "react-quill-new/dist/quill.snow.css";
import "react-quill-new/dist/quill.core.css";
import { UploadOutlined } from "@ant-design/icons";
import mammoth from "mammoth";
type FieldType = {
  jobName: string;
  jobDescription: string;
  division: string;
  selectionMark: number;
};

Quill.register("formats/list", true);
Quill.register("formats/bullet", true);
Quill.register("formats/blockquote", true);

const JobsForm: React.FC<{setOpen?: (open:string | null)=>void}> = ({setOpen}) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  form.resetFields();
  const notification = useAtomValue(notificationApiAtom);

  const beforeUpload = (file:any) => {
    const isDocx =
        file.type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

    if (!isDocx) {
      notification?.error({message:"Please upload a .docx file"});
      return Upload.LIST_IGNORE;
    }

    const reader = new FileReader();

    reader.onload = async (e: any) => {
      try {
        const arrayBuffer = e.target.result;

        // Convert Word → HTML (best for rich text editors)
        const result = await mammoth.convertToHtml({ arrayBuffer });
        form.setFieldsValue({
          jobDescription: result.value,
        });
      } catch (error) {
        notification?.error({message:"Failed to read Word document"});
      }
    };

    reader.readAsArrayBuffer(file);

    // Stop AntD from uploading
    return false;
  };
  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    try {
      const res = await addJob(values);
      queryClient.invalidateQueries({queryKey: ['allJobs']});
      notification?.success({message:`Job added successfully`});
      setOpen?.(null)
    } catch (error:AxiosError | any) {
      notification?.error({message: error?.response?.data?.detail || "Job addition failed!"});
    }
  };
  const { Option } = Select;
  const modules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      ["link", "blockquote", "code-block"],
      ["clean"],
    ],
    clipboard: {
      matchVisual: false,
    },
  };

  const formats = [
    "header",
    "bold",
    "italic",
    "underline",
    "strike",
    "list",
    "link",
    "blockquote",
    "code-block",
  ];
  return (
    <Form
      form={form}
      scrollToFirstError={{ behavior: 'instant', block: 'end', focus: true }}
      onFinish={onFinish}
      labelCol={{ span: 6 }}
      className="w-full"
    >
      <Form.Item
        name="division"
        label="Division"
        hasFeedback
        rules={[{ required: true, message: 'Please select a division!' }]}
      >
        <Select placeholder="Please select a division">
          <Option value="se">SE</Option>
          <Option value="qe">QE</Option>
          <Option value="devops">DevOps</Option>
        </Select>
      </Form.Item>
      <Form.Item<FieldType>
        label="Job Name"
        name="jobName"
        rules={[{ required: true, message: 'Please input your job name!' }]}
      >
        <Input />
      </Form.Item>
      <Form.Item<FieldType>
          label="Selection Mark"
          name="selectionMark"
          rules={[{ required: true, message: 'Please input a selection mark!' }]}
      >
        <InputNumber />
      </Form.Item>
      <Form.Item
          label={"Upload Job Description"}
      >

        <Upload beforeUpload={beforeUpload} showUploadList={false}>
          <Button icon={<UploadOutlined />}>Upload Word Document(.docx)</Button>
        </Upload>
      </Form.Item>
      <Form.Item name="jobDescription" label="Job Description"
        rules={[{ required: true, message: 'Please input a job description!' }]}
      >
        <ReactQuill
            modules={modules}
            formats={formats}
            theme="snow"
            placeholder="Type job description here..."
            style={{ minHeight: "200px" }}
        />
      </Form.Item>
      <div className="w-full p-2 flex flex-row justify-end">
        <Form.Item  className="m-0">
          <Flex gap="small">
            <Button type="primary" htmlType="submit">
              Submit
            </Button>
            <Button danger onClick={() => form.resetFields()}>
              Reset
            </Button>
          </Flex>
        </Form.Item>
      </div>
    </Form>
  );
};

export default JobsForm;
