import React from "react";
import { Button, Table, Tag, Drawer, Tooltip, Spin, Radio, Space, DatePicker } from "antd";
import { DeleteFilled, EditFilled, EyeFilled, GithubFilled, MailOutlined } from "@ant-design/icons";
import dayjs from 'dayjs';
import { fetchCvs, deleteCv, generateMark, sendSelectedMail, sendRejectedMail, exportCvsToExcel } from "../api";
import type { FormProps, TableProps } from 'antd';
import { useQuery, useQueryClient } from "@tanstack/react-query";
import CVFormEdit from "./CVFormEdit";
import CVForm from "./CVForm";
import { notificationApiAtom } from "../atoms";
import { useAtomValue } from "jotai";
import CVView from "./CVView";
import { CVGitStats } from "./CVGitStats";
import { interviewScheduledEmailSent, interviewScheduledEmailSentText, receivedEmailSent, receivedEmailSentText, rejectionEmailSent, rejectionEmailSentText, selectionEmailSent, selectionEmailSentText } from "../util/const";
import CVScheduleInterview from "./CVScheduleInterview";
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
  resumeContent: {[key: string]: {
    personal_info: {[key: string]: {
      name: string;
      email: string;
    }};
  }};
  finalMark: number;
  updatedAt: string;
  id: string | undefined;
  mailStatus?: string;
  interviewEvent?: {
    interviewName: string;
    interviewLocation: string;
    interviewAttendees: string[];
    interviewStartDatetime: string;
    interviewEndDatetime: string;
  }
}

type FieldType = {
  eventDateTime?: string;
  attendees?: string[];
  location?: string;
  event?: string;
};

const CV: React.FC = () => {
  const [open, setOpen] = React.useState<string | null>(null);
  const [ editData, setEditData] = React.useState<CVDataType | null>(null)
  const [ selectedRows, setSelectedRows] = React.useState<CVDataType[]>([])
  const [ selected, setSelected] = React.useState<boolean | null>(null)
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

  const sendMail = async(type: "selection" | "rejection") => {
    try {
      setLoading(true)
      const emails = selectedRows.map(row => {
        return {
          id: row.id,
          //@ts-ignore
          recipient_email: row.resumeContent.personal_info.email ?? "",
          //@ts-ignore
          candidate_name: row.resumeContent.personal_info.name ?? row.candidateName,
          position: row.jobName
        }
      })
      let res;
      if(type === "selection"){
        res = await sendSelectedMail(emails)
      }else{
        res = await sendRejectedMail(emails)
      }
      if(res.failed_emails.length > 0){
        notification?.warning({message:`Mail sending partially successful. Failed to send mail to: ${res.failed_emails.map((e:any) => e.recipient_email).join(", ")}`})
      }else{
        notification?.success({message:"Mail sent successfully to all recipients"})
      }
      queryClient.invalidateQueries({queryKey: ['allCVs']});
      setSelectedRows([])
    } catch (error) {
      notification?.error({message:"Mail sending failed"})
    }finally{
      setLoading(false)
      setSelectedRows([])
    }
    // return res.cvs
  }

  const exportToExcel = async() => {
    try {
      setLoading(true)
      const cvIds = selectedRows.map(row => row.id).filter(Boolean) as string[];
      
      if (cvIds.length === 0) {
        notification?.warning({message:"No CVs selected for export"});
        return;
      }
      
      await exportCvsToExcel(cvIds);
      notification?.success({message:`Successfully exported ${cvIds.length} CV(s) to Excel`});
    } catch (error) {
      notification?.error({message:"Excel export failed"});
    } finally {
      setLoading(false)
    }
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
      filters: Array.from(new Set(allCVs?.map(cv => cv.jobName)))
        .map(jobName => ({
          text: jobName,
          value: jobName
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
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const rangeKey = selectedKeys[0];
        const [start, end] = typeof rangeKey === 'string' ? rangeKey.split('|') : [];
        const pickerValue = start && end ? ([dayjs(start), dayjs(end)] as [dayjs.Dayjs, dayjs.Dayjs]) : null;

        return (
          <div style={{ padding: 8 }} className="flex flex-col">
            <DatePicker.RangePicker
              value={pickerValue}
              onChange={(dates) => {
                const startIso = dates?.[0]?.toISOString();
                const endIso = dates?.[1]?.toISOString();
                if (startIso && endIso) {
                  setSelectedKeys([`${startIso}|${endIso}`]);
                } else {
                  setSelectedKeys([]);
                }
              }}
              style={{ marginBottom: 8 }}
            />
            <Space>
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
        );
      },
      onFilter: (value, record) => {
        if (typeof value !== 'string' || !record.createdAt) return false;
        const [startIso, endIso] = value.split('|');
        if (!startIso || !endIso) return false;
        const recordDate = new Date(record.createdAt).getTime();
        const startDate = new Date(startIso).getTime();
        const endDate = new Date(endIso).getTime();
        return recordDate >= startDate && recordDate <= endDate;
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
      title: 'Email Status',
      key: 'mailStatus',
      dataIndex: 'mailStatus',
      filters: [
        {
          text: 'Received',
          value: 'received_email_sent',
        },
        {
          text: 'Selection',
          value: 'selection_email_sent',
        },
        {
          text: 'Rejection',
          value: 'rejection_email_sent'
        },
        {
          text: 'Interview Scheduled',
          value: 'interview_scheduled_email_sent'
        }
      ],
      onFilter: (value, record) => record?.mailStatus?.indexOf(value as string) === 0,
      render: (_, { mailStatus }) => {
        let color = 'blue';
        let displayText = "Received"
        if (mailStatus === receivedEmailSent) {
          color = 'blue';
          displayText = receivedEmailSentText
        }else if(mailStatus === selectionEmailSent){
          color = 'green'
          displayText = selectionEmailSentText
        }else if(mailStatus === rejectionEmailSent){
          color = 'volcano'
          displayText = rejectionEmailSentText
        }else if(mailStatus === interviewScheduledEmailSent){
          color = 'purple'
          displayText = interviewScheduledEmailSentText
        }
        return (
          <Tag color={color} key={mailStatus}>
            {displayText}
          </Tag>
        )
      },
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
          <Tooltip title="Schedule Interview">
              <Button
                type="link"
                icon={<MailOutlined />}
                disabled={record.mailStatus === rejectionEmailSent}
                // loading={loadings[3]}
                onClick={async () => {
                  setOpen("schedule_interview")
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


  return (
    <div className="w-full h-full flex flex-col justify-center items-center">
      {loding && <div className="fixed top-0 left-0 w-[100vw] h-[100vh] bg-black bg-opacity-15 z-20 flex justify-center items-center"><Spin size="large"/></div>}
      <div className="w-full p-2 flex flex-row justify-between">
        <div className="pb-2 flex flex-row justify-start">
          {/* <Form
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
          </Form> */}
        </div>
        <div className="flex gap-2">
          <Button onClick={exportToExcel} disabled={selectedRows.length === 0}>Export to Excel</Button>
          <Button onClick={() => sendMail("selection")} disabled={selectedRows.length === 0 || (!selected && selectedRows.length !==1)}>Send Selected Mail</Button>
          <Button onClick={() => sendMail("rejection")} disabled={selectedRows.length === 0}>Send Rejected Mail</Button>
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
            setSelected(selectedRows.filter(row => row.selectedForInterview === true).length === selectedRows.length)
          },
          getCheckboxProps: (record: CVDataType) => ({
            id: record.id,
          })
        }}
        pagination={{pageSize: 50}}
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
      <Drawer
        title="Schedule Interview"
        closable={{ 'aria-label': 'Close Button' }}
        onClose={onClose}
        open={open==='schedule_interview'}
        className="px-2"
        width={720}
      >
        <CVScheduleInterview setOpen={setOpen} editData={editData} setEditData={setEditData}/>
      </Drawer>
    </div>
  );
};

export default CV;
