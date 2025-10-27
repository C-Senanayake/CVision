import { atom } from 'jotai';
import type { NotificationInstance } from 'antd/es/notification/interface';

export const notificationApiAtom = atom<NotificationInstance | null>(null);
