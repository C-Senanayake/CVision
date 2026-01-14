import React from "react";
import { Button, Table, Tag, Form, Input, Drawer, Tooltip, Spin, Radio, Space } from "antd";
import { DeleteFilled, EditFilled, EyeFilled, GithubFilled } from "@ant-design/icons";
import { fetchCvs, deleteCv, generateMark } from "../api";
import type { FormProps, TableProps } from 'antd';
import { useQuery, useQueryClient } from "@tanstack/react-query";
import CVFormEdit from "./CVFormEdit";
import CVForm from "./CVForm";
import { notificationApiAtom } from "../atoms";
import { useAtomValue } from "jotai";
import CVView from "./CVView";
import { CVGitStats } from "./CVGitStats";

export interface CVDataType {
  key?: string;
  candidateName: string;
  jobName: string;
  division: string;
  createdAt?: string;
  cvName?: string;
  jobId?: string;
  markGenerated?: boolean;
  selectedForInterview?: boolean,
  comparisonResults?: {[key: string]: {
    mark: number;
    mark_fraction: string;
    explanation: string;
  }};
  finalMark: number;
  updatedAt: string;
  id: string | undefined;
}

type FieldType = {
  candidateName?: string;
};

const CV: React.FC = () => {
  const [open, setOpen] = React.useState<string | null>(null);
  const [ editData, setEditData] = React.useState<CVDataType | null>(null)
  const [ selectedRows, setSelectedRows] = React.useState<CVDataType[]>([])
  const [ loding, setLoading] = React.useState<boolean>(false)
  const notification = useAtomValue(notificationApiAtom);
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

  const generateRowMarks = async() => {
    try {
      setLoading(true)
      const res = await generateMark(selectedRows)
      queryClient.invalidateQueries({queryKey: ['allCVs']});
      setSelectedRows([])
      notification?.success({message:"Marks generated successfully"})
    } catch (error) {
      notification?.error({message:"Marks generation failed"})
    }finally{
      setLoading(false)
      setSelectedRows([])
    }
    
    // return res.cvs
  }

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
      title: 'Generated',
      dataIndex: 'markGenerated',
      key: 'markGenerated',
      render: (markGenerated:boolean) => (markGenerated ? <Tag color="green">Yes</Tag> : <Tag color="yellow">No</Tag>),
      sorter: (a, b) => (a?.markGenerated === b?.markGenerated ? 0 : a?.markGenerated ? -1 : 1),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
          <div style={{ padding: 8 }} className="flex flex-col">
            <Radio.Group
                value={selectedKeys[0]}
                onChange={(e:any) => setSelectedKeys([e.target.value])}
            >
              <Space direction="vertical">
                <Radio value={true}>Yes</Radio>
                <Radio value={false}>No</Radio>
              </Space>
            </Radio.Group>

            <Space style={{ marginTop: 8 }}>
              <Button
                  type="primary"
                  size="small"
                  onClick={() => confirm()}
              >
                Apply
              </Button>
              <Button
                  size="small"
                  onClick={() => {
                    clearFilters?.();
                    confirm();
                  }}
              >
                Reset
              </Button>
            </Space>
          </div>
      ),
      onFilter: (value, record) => record?.markGenerated === value || (record?.markGenerated === undefined && value === false),
    },
    {
      title: 'Mark',
      dataIndex: 'finalMark',
      key: 'finalMark',
      render: (text) => (text),
      sorter: (a, b) => a.finalMark - b.finalMark
    },
    {
      title: 'Selected',
      dataIndex: 'selectedForInterview',
      key: 'selectedForInterview',
      render: (selectedForInterview:boolean) => (selectedForInterview ? <Tag color="green">Yes</Tag> : <Tag color="yellow">No</Tag>),
      sorter: (a, b) => (a?.selectedForInterview === b?.selectedForInterview ? 0 : a?.selectedForInterview ? -1 : 1),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
          <div style={{ padding: 8 }} className="flex flex-col">
            <Radio.Group
                value={selectedKeys[0]}
                onChange={(e:any) => setSelectedKeys([e.target.value])}
            >
              <Space direction="vertical">
                <Radio value={true}>Yes</Radio>
                <Radio value={false}>No</Radio>
              </Space>
            </Radio.Group>

            <Space style={{ marginTop: 8 }}>
              <Button
                  type="primary"
                  size="small"
                  onClick={() => confirm()}
              >
                Apply
              </Button>
              <Button
                  size="small"
                  onClick={() => {
                    clearFilters?.();
                    confirm();
                  }}
              >
                Reset
              </Button>
            </Space>
          </div>
      ),
      onFilter: (value, record) => record?.selectedForInterview === value || (record?.selectedForInterview === undefined && value === false),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <>
          <Tooltip title={record.markGenerated ? "View Generated" : "Generation Pending"}>
              <Button
                type="link"
                icon={<EyeFilled />}
                disabled={!record.markGenerated}
                // loading={loadings[3]}
                onClick={() => {
                  setOpen("view")
                  setEditData(record)
                }}
              />
          </Tooltip>
          <Tooltip title="View Git Statistics">
              <Button
                type="link"
                icon={<GithubFilled />}
                disabled={!record.markGenerated}
                // loading={loadings[3]}
                onClick={() => {
                  setOpen("view_git_stat")
                  setEditData(record)
                }}
              />
          </Tooltip>
          <Tooltip title="Edit CV">
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
          <Tooltip title="Delete CV">
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
      {loding && <div className="fixed top-0 left-0 w-[100vw] h-[100vh] bg-black bg-opacity-15 z-20 flex justify-center items-center"><Spin size="large"/></div>}
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
        <div className="flex gap-2">
          <Button onClick={generateRowMarks} disabled={selectedRows.length === 0}>Generate</Button>
          <Button onClick={showDrawer}>Add New</Button>
        </div>
      </div>
      <Table<CVDataType> 
        className="w-full h-full overflow-y-auto overflow-x-hidden" 
        loading={isLoading} 
        columns={columns} 
        dataSource={allCVs}
        rowKey="id"
        rowSelection={{ 
          type: 'checkbox', 
          onChange: (_selectedRowKeys: React.Key[], selectedRows: CVDataType[]) => {
            setSelectedRows(selectedRows)
          },
          getCheckboxProps: (record: CVDataType) => ({
            id: record.id,
          })
        }}
      />
      <Drawer
        title="Upload CV"
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
      <Drawer
        title="View"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='view'}
        className="p-0"
        width={"100%"}
      >
        <CVView data={editData}/>
      </Drawer>
      <Drawer
        title="View Git Statistics"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='view_git_stat'}
        className="p-0"
        width={"100%"}
      >
        <CVGitStats cvData={editData}/>
      </Drawer>
    </div>
  );
};

export default CV;
