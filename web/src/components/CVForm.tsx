import React from "react";
import { Upload, Button, Form, Flex, Select, Spin } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import type { RcFile } from "antd/lib/upload";
import { fetchJob, uploadCv } from "../api";
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import type { DataType } from "./Jobs";
import type { GetProp, UploadFile, UploadProps, FormProps } from 'antd';

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

type FieldType = {
  jobName: string;
  cvFiles: string
};

const CVForm: React.FC<{setOpen?: (open:string | null)=>void, open: string | null}> = ({setOpen, open}) => {
  const [fileList, setFileList] = React.useState<UploadFile[]>([]);
  const [loading, setLoading] = React.useState(false)
  const {data: allJobs, isLoading} = useQuery<DataType[]>({
      queryKey: ['allJobsSelection'],
      queryFn: async () => {
          const res = await fetchJob()
          return res.jobs
      },
      staleTime: 1000
  })
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  React.useEffect(()=>{
    form.resetFields();
    setFileList([])
  },[open])
  const notification = useAtomValue(notificationApiAtom);

  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    const formData = new FormData();
    if(fileList.length === 0){
      notification?.error({message:"Please upload atleast one file"});
      return;
    }
    fileList.forEach((file) => {
      formData.append('files', file as FileType);
    });
    const [division, jobName, id] = (values.jobName as string).split("_")
    formData.append('division',division);
    formData.append('jobName',jobName);
    formData.append('id',id);
    try {
      setLoading(true)
      const res = await uploadCv(formData);
      if(res?.statusCode === 200){
        queryClient.invalidateQueries({queryKey: ['allCVs']});
        notification?.success({message:`CV/s uploaded successfully`});
      }else{
        notification?.error({message: res?.detail || "CV/s upload failed!"});
      }
    } catch (error:AxiosError | any) {
      notification?.error({message: error?.response?.data?.detail || "CV/s upload failed!"});
    }
    finally{
      setOpen?.(null)
      setLoading(false)
    }
  };

  const beforeUpload = (file: RcFile) => {
    const isPdfOrZip =
      file.type === "application/pdf" ||
      file.type === "application/x-zip-compressed" ||
      file.name.endsWith(".zip");

    if (!isPdfOrZip) {
      notification?.error({message:"You can only upload PDF or ZIP files!"});
    }else{
      setFileList([...fileList, file]);
    }

    return isPdfOrZip || Upload.LIST_IGNORE;
  };

  const { Option } = Select;
  return (
    <>
      {loading &&<div className="w-full h-full absolute top-0 left-0 bg-gray-200 opacity-50 z-10 flex justify-center items-center">
        <Spin size="large"/>
      </div>}
      <Form
        form={form}
        scrollToFirstError={{ behavior: 'instant', block: 'end', focus: true }}
        // style={{ paddingBlock: 32 }}
        // wrapperCol={{ span: 24 }}
        onFinish={onFinish}
        labelCol={{ span: 6 }}
        className="w-full"
      >
        <Form.Item
          name="jobName"
          label="Job Name"
          hasFeedback
          rules={[{ required: true, message: 'Please select a job!' }]}
        >
          <Select placeholder="Please select a job" loading={isLoading}>
            {allJobs?.map(job=>(
              <Option key={job.id} value={`${job.division}_${job.jobName}_${job.id}`}>{job.jobName}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item<FieldType>
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
    </>
  );
};

export default CVForm;
