import { Layout, Menu } from 'antd';
import { useCallback } from 'react';
import {
    BrowserRouter,
    Routes,
    Route,
    useNavigate,
    useLocation,
    Link,
} from "react-router-dom";
const { Content, Footer } = Layout;
function App() {
  const items = [
    {
      key: '/',
      label: 'Job Description',
    },
    {
      key: '/cv',
      label: 'CV',
    },
  ];

  return (
    <BrowserRouter>
      <MainLayout items={items} />
    </BrowserRouter>
  );
}

function MainLayout({ items }: { items: { key: string; label: string }[] }) {
  const navigate = useNavigate();
  const location = useLocation();
  const setView = useCallback((view: string) => {
        navigate(view)
    }, []);
  return (
    <Layout className="h-[100vh]">
      <Layout.Header className={"flex flex-row items-center justify-start border-b border-solid border-x-gray-500 pl-3 pr-0 bg-white"}>
          <div className="flex flex-row justify-between items-center ">
              <div className="flex w-14 h-full items-center">
                  <Link to="/">
                      <img src='/logo.png' className="bg-transparent p-0" alt={"logo"} />
                  </Link>
              </div>
              <div className="w-px h-9 border" />
          </div>
          <Menu
              theme="light"
              mode="horizontal"
              // defaultSelectedKeys={['/job_description']}
              items={items}
              style={{ width: "100vw" }}
              className="flex-auto user-menu"
              onSelect={(e) => {
                  setView(e.key)
              }}
              selectedKeys={[location.pathname]}
          />
      </Layout.Header>

      <Content style={{ padding: '0 48px' }}>
        <Routes>
          <Route path="/" element={<>Job Description Page</>} />
          <Route path="/cv" element={<>CV Page</>} />
        </Routes>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        CVision ©{new Date().getFullYear()} Created by QGENIUS
      </Footer>
    </Layout>
  );
}

export default App
