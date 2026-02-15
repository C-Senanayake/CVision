import React from "react";
import { Button, Form, Flex, Input, DatePicker } from "antd";
import dayjs from 'dayjs';
import { sendInterviewScheduledMail } from "../api";
import type { FormProps } from 'antd';
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import type { CVDataType } from "./CV";
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.tz.setDefault('Asia/Kolkata')

const { RangePicker } = DatePicker;

type FieldType = {
  eventDateTime?: string;
  attendees?: string;
  location?: string;
  event?: string;
};

interface FormEditProps{
  setOpen: (open:string | null)=>void
  editData: CVDataType | null
  setEditData: (data:CVDataType | null)=>void
}

const CVScheduleInterview: React.FC<FormEditProps> = ({setOpen, editData, setEditData}) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  
  form.setFieldsValue({
    event: editData?.interviewEvent?.interviewName,
    location: editData?.interviewEvent?.interviewLocation,
    attendees: editData?.interviewEvent?.interviewAttendees?.join(","),
    eventDateTime: editData?.interviewEvent?.interviewStartDatetime && editData?.interviewEvent?.interviewEndDatetime 
      ? [dayjs.tz(editData.interviewEvent.interviewStartDatetime), dayjs.tz(editData.interviewEvent.interviewEndDatetime)] 
      : null
  });
  const notification = useAtomValue(notificationApiAtom);
  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    
    const eventDateTime = form.getFieldValue('eventDateTime');
    const startDatetime = eventDateTime?.[0]?.add(5, 'hour')?.add(30, 'minute')?.toISOString();
    const endDatetime = eventDateTime?.[1]?.add(5, 'hour')?.add(30, 'minute')?.toISOString();
    
    try {
      const data = {
        id:editData?.id,
        //@ts-ignore
        recipient_email:editData?.resumeContent?.personal_info?.email,
        //@ts-ignore
        candidate_name:editData?.resumeContent?.personal_info?.name,
        position:editData?.jobName,
        event:values?.event,
        start_datetime:startDatetime,
        end_datetime:endDatetime,
        location:values?.location,
        attendees:values?.attendees?.split(",").map((email: string) => email.trim())
      }
      await sendInterviewScheduledMail(data);
      queryClient.invalidateQueries({queryKey: ['allCVs']});
      notification?.success({message:`Interview scheduling email sent successfully`});
    } catch (error:AxiosError | any) {
      notification?.error({message: error?.response?.data?.detail || "Interview scheduling failed!"});
    }
    finally{
      setOpen(null)
      setEditData(null)
    }
  };
  return (
    <Form
      form={form}
      scrollToFirstError={{ behavior: 'instant', block: 'end', focus: true }}
      onFinish={onFinish}
      labelCol={{ span: 6 }}
      className="w-full"
    >
      <Form.Item<FieldType>
        label="Event"
        name="event"
        rules={[{ required: true, message: 'Please enter event name' }]}
      >
        <Input placeholder="e.g. Technical Interview, HR Interview, etc."/>
      </Form.Item>
      <Form.Item<FieldType>
        label="Location"
        name="location"
      >
        <Input placeholder="e.g. Google maps location"/>
      </Form.Item>
      <Form.Item<FieldType>
        label="Attendees"
        name="attendees"
      >
        <Input placeholder="Enter additional attendee emails separated by commas"/>
      </Form.Item>
      <Form.Item<FieldType>
        label="Event Date & Time"
        name="eventDateTime"
        rules={[{ required: true, message: 'Please select start and end date and time!' }]}
      >
        <RangePicker
          showTime={{ format: 'HH:mm' }}
          format="YYYY-MM-DD HH:mm"
          style={{ width: '100%' }}
          disabledDate={(current) => current && current < dayjs().startOf('day')}
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

export default CVScheduleInterview;
