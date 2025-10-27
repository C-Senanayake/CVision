import React from "react";
import { Button, Form, Flex, Select } from "antd";
import { fetchJob, updateCv } from "../api";
import type { FormProps } from 'antd';
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import type { CVDataType } from "./CV";
import type { DataType } from "./Jobs";

type FieldType = {
  jobName: string;
  jobDescription: string;
  division: string
};

interface FormEditProps{
  setOpen: (open:string | null)=>void
  editData: CVDataType | null
  setEditData: (data:CVDataType | null)=>void
}

const CVFormEdit: React.FC<FormEditProps> = ({setOpen, editData, setEditData}) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  form.setFieldsValue({
    candidateName: editData?.candidateName,
    division: editData?.division,
    jobName: editData?.jobName,
  });
  const notification = useAtomValue(notificationApiAtom);
  const {data: allJobs, isLoading} = useQuery<DataType[]>({
      queryKey: ['allJobsSelection'],
      queryFn: async () => {
          const res = await fetchJob()
          return res.jobs
      },
      staleTime: 1000
  })
  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    try {
      const [division, jobName, jobId] = (values.jobName as string).split("_")
      const res = await updateCv({division, jobName, jobId, id: editData?.id});
      queryClient.invalidateQueries({queryKey: ['allCVs']});
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
      className="w-full"
    >
      <Form.Item
        name="jobName"
        label="Job Name"
        hasFeedback
        rules={[{ required: true, message: 'Please select a job!' }]}
        initialValue={`${editData?.division}_${editData?.jobName}_${editData?.jobId}`}
      >
        <Select placeholder="Please select a job" loading={isLoading}>
          {allJobs?.map(job=>(
            <Option key={job.id} value={`${job.division}_${job.jobName}_${job.id}`}>{job.jobName}</Option>
          ))}
        </Select>
      </Form.Item>
      {/* <Form.Item<FieldType>
        label="Upload CV/s"
        name="cvFiles"
        rules={[{ required: true, message: 'Please upload 1 or more files!' }]}
      >
        <Upload
          customRequest={({ onSuccess }) => {
              setTimeout(() => {
                  onSuccess?.('ok');
              }, 0);
          }}
          fileList={fileList}
          beforeUpload={beforeUpload}
          onRemove={(file)=>{
            const index = fileList.indexOf(file);
            const newFileList = fileList.slice();
            newFileList.splice(index, 1);
            setFileList(newFileList);
          }}
          // multiple={false}
          showUploadList={true}
        >
          <Button icon={<UploadOutlined />}>Click to Upload PDF or ZIP</Button>
        </Upload>
      </Form.Item> */}
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

export default CVFormEdit;
