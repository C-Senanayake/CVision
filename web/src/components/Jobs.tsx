import React from "react";
import { Button, Table, Tag, Form, Input, Drawer, Tooltip, Segmented } from "antd";
import { DeleteFilled, EditFilled, EyeFilled } from "@ant-design/icons";
import { fetchJob, deleteJob } from "../api";
import type { FormProps, RadioChangeEvent, TableProps } from 'antd';
import JobsForm from "./JobsForm";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import JobsFormEdit from "./JobsFormEdit";
import JobsFormCriteria from "./JobsFormCriteria";

export interface DataType {
  key?: string;
  jobName: string;
  division: string;
  jobDescription?: string;
  criteria?: {
    [k: string]: string;
  };
  createdAt?: string;
  updatedAt?: string;
  id: string | undefined;
  selectionMark: number
}

type FieldType = {
  jobName?: string;
};

const Jobs: React.FC = () => {
  const [open, setOpen] = React.useState<string | null>(null);
  const [ editData, setEditData] = React.useState<DataType | null>(null)
  const [mode, setMode] = React.useState<'Basic Info' | 'Criteria'>('Basic Info');

  const handleModeChange = (e: RadioChangeEvent) => {
    setMode(e.target.value);
  };
  const queryClient = useQueryClient();
  // const [data, setData] = React.useState<DataType[]>([])
  const showDrawer = () => {
    setOpen('add');
  };

  const onClose = () => {
    setOpen(null);
    setEditData(null)
  };

  const {data: allJobs, isLoading} = useQuery<DataType[]>({
      queryKey: ['allJobs'],
      queryFn: async () => {
          const res = await fetchJob()
          return res.jobs
      }
  })

  const columns: TableProps<DataType>['columns'] = [
    {
      title: 'Job Name',
      dataIndex: 'jobName',
      key: 'jobName',
      render: (text) => (text),
      sorter: (a, b) => a.jobName.localeCompare(b.jobName),
      filters: allJobs?.map(job => ({
        text: job.jobName,
        value: job.jobName
      })),
      onFilter: (value, record) => record.jobName.indexOf(value as string) === 0,
    },
    {
      title: 'Division',
      key: 'division',
      dataIndex: 'division',
      filters: [
        {
          text: 'QE',
          value: 'qe',
        },
        {
          text: 'Software',
          value: 'se',
        },
        {
          text: 'DevOps',
          value: 'devops'
        }
      ],
      onFilter: (value, record) => record.division.indexOf(value as string) === 0,
      render: (_, { division }) => {
        let color = 'green';
        if (division === 'se') {
          color = 'volcano';
        }else if(division === 'qe'){
          color = 'blue'
        }else if(division === 'devops'){
          color = 'green'
        }
        return (
          <Tag color={color} key={division}>
            {division.toUpperCase()}
          </Tag>
        )
      },
    },
    {
      title: 'Created Date',
      key: 'createdAt',
      dataIndex: 'createdAt',
      sorter: (a, b) => {
        const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
        const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
        return dateA - dateB;
      },
      render: (_, { createdAt }) => {
        return (
          <span>
            {createdAt ? new Date(createdAt).toLocaleDateString() : "-"}
          </span>
        );
      },
    },
    {
      title: 'Updated Date',
      key: 'updatedAt',
      dataIndex: 'updatedAt',
      sorter: (a, b) => {
        const dateA = a.updatedAt ? new Date(a.updatedAt).getTime() : 0;
        const dateB = b.updatedAt ? new Date(b.updatedAt).getTime() : 0;
        return dateA - dateB;
      },
      render: (_, { updatedAt }) => {
        return (
          <span>
            {updatedAt ? new Date(updatedAt).toLocaleDateString() : "-"}
          </span>
        );
      },
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <>
          <Tooltip title="View Job">
            <Button
              type="link"
              icon={<EyeFilled />}
              // loading={loadings[3]}
              onClick={() => {
                setOpen("view")
                setEditData(record)
                setMode("Basic Info")
              }}
            />
          </Tooltip>
          <Tooltip title="Edit Job">
              <Button
                type="link"
                icon={<EditFilled />}
                // loading={loadings[3]}
                onClick={() => {
                  setOpen("edit")
                  setEditData(record)
                  setMode("Basic Info")
                }}
              />
          </Tooltip>
          <Tooltip title="Delete Job">
              <Button
                type="link"
                icon={<DeleteFilled />}
                danger
                // loading={loadings[3]}
                onClick={async () => {
                  await deleteJob(record.id)
                  queryClient.invalidateQueries({queryKey: ['allJobs']});
                }}
              />
          </Tooltip>
        </>
      ),
    },
  ];

  const onFinish: FormProps<FieldType>['onFinish'] = (values) => {
    console.log('Success:', values);
  };

  return (
    <div className="w-full h-full flex flex-col justify-center items-center">
      <div className="w-full p-2 flex flex-row justify-between">
        <div className="pb-2 flex flex-row justify-start">
          <Form
            name="basic"
            labelCol={{ span: 8 }}
            wrapperCol={{ span: 16 }}
            style={{ maxWidth: 600 }}
            initialValues={{ remember: true }}
            onFinish={onFinish}
            autoComplete="off"
            layout="inline"
          >
            <Form.Item<FieldType>
              label="Job Name"
              name="jobName"
              // rules={[{ required: true, message: 'Please input your job name!' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item label={null}>
              <Button type="primary" htmlType="submit">
                Filter
              </Button>
            </Form.Item>
          </Form>
        </div>
        <Button onClick={showDrawer}>Add New</Button>
      </div>
      <Table<DataType> className="w-full h-full overflow-y-auto overflow-x-hidden" loading={isLoading} columns={columns} dataSource={allJobs}/>
      <Drawer
        title="Add New Job"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='add'}
        className="px-2"
        width={720}
      >
        <JobsForm setOpen={setOpen}/>
      </Drawer>
      <Drawer
        title="Edit Job"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='edit'}
        className="px-2"
        width={720}
      >
        <Segmented<string>
          options={['Basic Info', 'Criteria']}
          onChange={(value:string) => {
            setMode(value as 'Basic Info' | 'Criteria')
          }}
          value={mode}
          block={true}
          size="large"
          className="w-full absolute top-14 left-0 z-10"
        />
        {mode === "Basic Info" ? <JobsFormEdit setOpen={setOpen} editData={editData} setEditData={setEditData}/>
         : <JobsFormCriteria setOpen={setOpen} editData={editData} setEditData={setEditData}/>}
      </Drawer>
      <Drawer
        title="View Job"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open === 'view'}
        className="px-2"
        width={720}
      >
        <Segmented<string>
          options={['Basic Info', 'Criteria']}
          onChange={(value:string) => {
            setMode(value as 'Basic Info' | 'Criteria')
          }}
          value={mode}
          block={true}
          size="large"
          className="w-full absolute top-14 left-0 z-10"
        />
        {mode === "Basic Info" ? <JobsFormEdit setOpen={setOpen} editData={editData} setEditData={setEditData} viewOnly={true}/>
         : <JobsFormCriteria setOpen={setOpen} editData={editData} setEditData={setEditData} viewOnly={true}/>}
      </Drawer>
    </div>
  );
};

export default Jobs;
