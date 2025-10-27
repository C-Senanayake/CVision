import { useSetAtom } from 'jotai';
import { notification } from 'antd';
import React from 'react';
import { notificationApiAtom } from '../../atoms/notificationApiAtom';

export const NotificationInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [api, contextHolder] = notification.useNotification();
    const setNotificationApi = useSetAtom(notificationApiAtom);

    React.useEffect(() => {
        setNotificationApi(api);
    }, [api, setNotificationApi]);

    return (
        <>
            {contextHolder}
            {children}
        </>
    );
};