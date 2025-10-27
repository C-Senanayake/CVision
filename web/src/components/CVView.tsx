import React from "react";
import { Splitter, Card, Col, Typography } from "antd";
import { fetchCvPdf } from "../api";
import { useQuery } from "@tanstack/react-query";
import type { CVDataType } from "./CV";

const { Title } = Typography;

interface FormEditProps{
  data: CVDataType | null
}

const CVView: React.FC<FormEditProps> = ({data}) => {
  console.log("EDIT::",data);
  const {data: fileUrl, isLoading} = useQuery<string>({
      queryKey: ["fileUrl", data?.id, data?.cvName],
      queryFn: async () => {
          const res = await fetchCvPdf(data?.id, data?.cvName)
          return res
      },
      staleTime: 1000
  })

  return (
    <Splitter style={{ height: "100%", boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
      <Splitter.Panel defaultSize="70%" min="20%" max="70%">
        <div className="w-full h-full">
          {!isLoading && fileUrl && <iframe
            src={fileUrl}
            style={{ width: "100%", height:"100%", border: "none" }}
            title="CV PDF Viewer"
          />}
        </div>
      </Splitter.Panel>
      <Splitter.Panel>
        <div className="pt-2 bg-green-300 flex items-center justify-center">
          <Title level={2} className="text-center">
            Total Marks: <b>{data?.finalMark}</b>
          </Title>
        </div>
        <div className="px-6 py-4">
          {data?.comparisonResults && Object.entries(data?.comparisonResults).map(([key, value]) => (
            <Col className="w-full">
              <Card title={
                <div className="flex row justify-between">
                  <p>{key}</p>
                  <p>Mark-{value.mark_fraction}</p>
                </div>
              } type="inner" className="mb-4 shadow-md">
                <p>{value.explanation}</p>
              </Card>
            </Col>
          ))}
        </div>
      </Splitter.Panel>
    </Splitter>
  )
};

export default CVView;
