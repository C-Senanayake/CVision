import React from "react";
import { Button, Form, Input, Flex, Select } from "antd";
import { updateJob } from "../api";
import type { FormProps } from 'antd';
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import type { DataType } from "./Jobs";

type FieldType = {
  jobName: string;
  jobDescription: string;
  division: string
};

interface FormEditProps{
  setOpen: (open:string | null)=>void
  editData: DataType | null
  setEditData: (data:DataType | null)=>void
}

const JobsFormEdit: React.FC<FormEditProps> = ({setOpen, editData, setEditData}) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  form.setFieldsValue({
    division: editData?.division,
    jobName: editData?.jobName,
    jobDescription: editData?.jobDescription,
  });
  const notification = useAtomValue(notificationApiAtom);

  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    try {
      const res = await updateJob({...values, id: editData?.id});
      queryClient.invalidateQueries({queryKey: ['allJobs']});
      notification?.success({message:`Job updated successfully`});
    } catch (error:AxiosError | any) {
      notification?.error({message: error?.response?.data?.detail || "Job update failed!"});
    }
    finally{
      setOpen(null)
      setEditData(null)
    }
  };
  const { Option } = Select;
  return (
    <Form
      form={form}
      scrollToFirstError={{ behavior: 'instant', block: 'end', focus: true }}
      onFinish={onFinish}
      labelCol={{ span: 4 }}
      className="w-full mt-8"
    >
      <Form.Item
        name="division"
        label="Division"
        hasFeedback
        rules={[{ required: true, message: 'Please select a division!' }]}
        initialValue={editData?.division}
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
        initialValue={editData?.jobName}
      >
        <Input disabled/>
      </Form.Item>
      <Form.Item name="jobDescription" label="Job Description" initialValue={editData?.jobDescription}
        rules={[{ required: true, message: 'Please input a job description!' }]}
      >
        <Input.TextArea rows={20} required />
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

export default JobsFormEdit;
