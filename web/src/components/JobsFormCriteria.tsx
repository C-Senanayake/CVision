import React from "react";
import { Button, Form, Input, Flex, InputNumber } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { updateJobCriteria } from "../api";
import type { FormProps } from 'antd';
import { useAtomValue } from "jotai";
import { notificationApiAtom } from "../atoms";
import { useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import type { DataType } from "./Jobs";

type FieldType = {
  criteria: Array<{
    criteriaName: string;
    criteriaPercentage: string;
  }>
};

interface FormEditProps{
  setOpen: (open:string | null)=>void
  editData: DataType | null
  setEditData: (data:DataType | null)=>void
}

const JobsFormCriteria: React.FC<FormEditProps> = ({setOpen, editData, setEditData}) => {
  const [totalPercentage, setTotalPercentage] = React.useState(0);

  const calculateTotal = () => {
    const criteria = form.getFieldValue('criteria') || [];
    const total = criteria.reduce((sum:number, item:any) => {
      return sum + (parseFloat(item?.criteriaPercentage) || 0);
    }, 0);
    setTotalPercentage(total);
    return total;
  };

  const [form] = Form.useForm();
  const populateForm = (criteriaObject: {[k: string]: string;}) => {
    const criteriaArray = Object.entries(criteriaObject).map(([key, value]) => ({
      criteriaName: key,
      criteriaPercentage: value
    }));

    form.setFieldsValue({
      criteria: criteriaArray
    });

    calculateTotal();
  };

  React.useEffect(() => {
    populateForm(editData?.criteria || {});
  }, []);
  
  const queryClient = useQueryClient();
  // form.resetFields();
  form.setFieldsValue({
    division: editData?.division,
    jobName: editData?.jobName,
    jobDescription: editData?.jobDescription,
  });
  const notification = useAtomValue(notificationApiAtom);

  const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
    try {
      const obj = Object.fromEntries(
        values?.criteria.map(item => [item.criteriaName, item.criteriaPercentage])
      );
      await updateJobCriteria({id: editData?.id, criteria: obj});
      queryClient.invalidateQueries({queryKey: ['allJobs']});
      notification?.success({message:`Job updated successfully`});
    } catch (error:AxiosError | any) {
      notification?.error({message: error?.response?.data?.detail || "Job update failed!"});
    } finally {
      setOpen(null)
      setEditData(null)
      setTotalPercentage(0)
      form.resetFields()
    }
  };
  return (
    <Form
      form={form}
      scrollToFirstError={{ behavior: 'instant', block: 'end', focus: true }}
      // style={{ paddingBlock: 32 }}
      // wrapperCol={{ span: 24 }}
      onFinish={onFinish}
      className="w-full mt-8 flex flex-col"
    >
      <Form.List name="criteria">
      {(fields, { add, remove }) => (
        <>
          {fields.map(({ key, name, ...restField }) => (
            <div key={key} style={{ display: 'flex', marginBottom: 8, width: '100%', alignItems: 'baseline', gap: 8 }} >
              <Form.Item
                {...restField}
                name={[name, 'criteriaName']}
                rules={[{ required: true, message: 'Missing criteria name' }]}
                style={{ flex: '0 0 70%', marginBottom: 0 }}
              >
                <Input placeholder="Criteria Name" />
              </Form.Item>
              <Form.Item
                {...restField}
                name={[name, 'criteriaPercentage']}
                rules={[{ required: true, message: 'Missing percentage' }]}
                style={{ flex: '0 0 25%', marginBottom: 0 }}
              >
                <InputNumber style={{ width: '100%' }} min={0} max={1} step={0.1} placeholder="Criteria Percentage" onChange={calculateTotal}/>
              </Form.Item>
              <MinusCircleOutlined onClick={() => {
                remove(name)
                calculateTotal()
              }}/>
            </div>
          ))}
          <div style={{ 
            marginBottom: 16, 
            padding: '8px 12px', 
            backgroundColor: totalPercentage > 1 ? '#fff2f0' : '#f6ffed',
            border: `1px solid ${totalPercentage > 1 ? '#ffccc7' : '#b7eb8f'}`,
            borderRadius: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ fontWeight: 'bold' }}>Total Percentage:</span>
            <span style={{ 
              fontWeight: 'bold', 
              color: totalPercentage > 1 ? '#cf1322' : '#52c41a',
              fontSize: '16px'
            }}>
              {(totalPercentage * 100).toFixed(1)}%
            </span>
          </div>
          <Form.Item>
            <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
              Add criteria
            </Button>
          </Form.Item>
        </>
      )}
    </Form.List>
      <div className="w-full p-2 flex flex-row justify-end">
        <Form.Item  className="m-0">
          <Flex gap="small">
            <Button type="primary" htmlType="submit" disabled={totalPercentage === 0}>
              Submit
            </Button>
            <Button danger disabled={totalPercentage === 0} onClick={() => {
              form.resetFields()
              setTotalPercentage(0)
            }}>
              Reset
            </Button>
          </Flex>
        </Form.Item>
      </div>
    </Form>
  );
};

export default JobsFormCriteria;
