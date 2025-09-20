import React from "react";
import { Upload, Button, message } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import type { RcFile } from "antd/lib/upload";
import { uploadFile } from "../api";

const FileUpload: React.FC = () => {
  const beforeUpload = (file: RcFile) => {
    const isPdfOrZip =
      file.type === "application/pdf" ||
      file.type === "application/x-zip-compressed" ||
      file.name.endsWith(".zip");

    if (!isPdfOrZip) {
      message.error("You can only upload PDF or ZIP files!");
    }

    return isPdfOrZip || Upload.LIST_IGNORE;
  };

  const handleUpload = async (file: RcFile) => {
    try {
      const res = await uploadFile(file);
      message.success(`File uploaded successfully: ${res.filename}`);
      console.log(res);
    } catch (error) {
      message.error("Upload failed!");
    }
  };

  return (
    <Upload
      customRequest={({ file, onSuccess }) => {
        handleUpload(file as RcFile).then(() => onSuccess && onSuccess("ok"));
      }}
      beforeUpload={beforeUpload}
      multiple={false}
      showUploadList={true}
    >
      <Button icon={<UploadOutlined />}>Click to Upload PDF or ZIP</Button>
    </Upload>
  );
};

export default FileUpload;
