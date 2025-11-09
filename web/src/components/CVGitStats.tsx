import { useEffect, useState, type FunctionComponent } from 'react'
import { Pie } from '@ant-design/charts'
import type { CVDataType } from './CV'
import { fetchGitHubData } from '../api';
import type { GitHubData, GitHubLanguage } from '../util/types';

interface FormEditProps{
  cvData: CVDataType | null
}

export const CVGitStats:FunctionComponent<FormEditProps> = ({cvData}) => {
  const [gitHubData, setGitHubData] = useState<GitHubData>();
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    setLoading(true)
    fetchGitHubData(cvData?.id)
    .then((data) => {
      setGitHubData(data)
      console.log(data);
    })
    setLoading(false)
  }, [cvData])

  const config = {
    data: gitHubData?.statistics.languages.languages.map((lang: GitHubLanguage) => {
      return {type: lang.language, value: lang.repo_count}
    }) || [],
    angleField: 'value',
    colorField: 'type',
    innerRadius: 0.6,
    label: {
      text: 'value',
      style: {
        fontWeight: 'bold',
      },
    },
    legend: {
      color: {
        title: false,
        position: 'right',
        rowPadding: 5,
      },
    },
    annotations: [
      {
        type: 'text',
        style: {
          text: 'Top \nLanguages\n by Repo',
          x: '50%',
          y: '50%',
          textAlign: 'center',
          fontSize: 20,
          fontStyle: 'bold',
        },
      },
    ],
  };

  return <div>
    <div style={{width: "50%"}}>
      <Pie 
        loading={loading}
        {...config}
      />
    </div> 
    <div>
      <div>Joined GitHub {gitHubData?.statistics.account_age_years} ago</div>
    </div>
  </div>
}
