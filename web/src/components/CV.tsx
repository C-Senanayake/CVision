import React from "react";
import { Button, Table, Tag, Form, Input, Drawer, Tooltip } from "antd";
import { DeleteFilled, EditFilled } from "@ant-design/icons";
import { fetchCvs, deleteCv } from "../api";
import type { FormProps, TableProps } from 'antd';
import { useQuery, useQueryClient } from "@tanstack/react-query";
import CVFormEdit from "./CVFormEdit";
import CVForm from "./CVForm";

export interface CVDataType {
  key?: string;
  candidateName: string;
  jobName: string;
  division: string;
  createdAt?: string;
  updatedAt?: string;
  id: string | undefined;
}

type FieldType = {
  candidateName?: string;
};

const CV: React.FC = () => {
  const [open, setOpen] = React.useState<string | null>(null);
  const [ editData, setEditData] = React.useState<CVDataType | null>(null)
  const [ selectedRows, setSelectedRows] = React.useState<CVDataType[]>([])
  const queryClient = useQueryClient();
  const showDrawer = () => {
    setOpen('add');
  };

  const onClose = () => {
    setOpen(null);
    setEditData(null)
  };

  const {data: allCVs, isLoading} = useQuery<CVDataType[]>({
      queryKey: ['allCVs'],
      queryFn: async () => {
          const res = await fetchCvs()
          return res.cvs
      }
  })

  const columns: TableProps<CVDataType>['columns'] = [
    {
      title: 'Candidate Name',
      dataIndex: 'candidateName',
      key: 'candidateName',
      render: (text) => (text),
      sorter: (a, b) => a.candidateName.localeCompare(b.candidateName),
      filters: allCVs?.map(cv => ({
        text: cv.candidateName,
        value: cv.candidateName
      })),
      onFilter: (value, record) => record.candidateName.indexOf(value as string) === 0,
    },
    {
      title: 'Job Name',
      dataIndex: 'jobName',
      key: 'jobName',
      render: (text) => (text),
      sorter: (a, b) => a.jobName.localeCompare(b.jobName),
      filters: allCVs?.map(cv => ({
        text: cv.jobName,
        value: cv.jobName
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
          <Tooltip title="Delete Job">
              <Button
                type="link"
                icon={<EditFilled />}
                // loading={loadings[3]}
                onClick={() => {
                  setOpen("edit")
                  setEditData(record)
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
                  await deleteCv(record.id)
                  queryClient.invalidateQueries({queryKey: ['allCVs']});
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
            initialValues={{ remember: true }}
            onFinish={onFinish}
            autoComplete="off"
            layout="inline"
          >
            <Form.Item<FieldType>
              label="Candidate Name"
              name="candidateName"
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
      <Table<CVDataType> 
        className="w-full h-full overflow-y-auto overflow-x-hidden" 
        loading={isLoading} 
        columns={columns} 
        dataSource={allCVs}
        rowKey="id"
        rowSelection={{ 
          type: 'checkbox', 
          onChange: (selectedRowKeys: React.Key[], selectedRows: CVDataType[]) => {
            console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
            setSelectedRows(selectedRows)
          },
          getCheckboxProps: (record: CVDataType) => ({
            id: record.id,
          })
        }}
      />
      <Drawer
        title="Add New Job"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='add'}
        className="p-0"
        width={500}
      >
        <CVForm setOpen={setOpen} open={open}/>
      </Drawer>
      <Drawer
        title="Edit Job"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='edit'}
        className="px-2"
        width={720}
      >
        <CVFormEdit setOpen={setOpen} editData={editData} setEditData={setEditData}/>
      </Drawer>
    </div>
  );
};

export default CV;
