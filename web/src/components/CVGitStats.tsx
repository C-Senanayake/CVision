import { useEffect, useState, type FunctionComponent } from "react";
import { Pie } from "@ant-design/charts";
import type { CVDataType } from "./CV";
import { fetchGitHubData } from "../api";
import type { GitHubData, GitHubLanguage } from "../util/types";

interface FormEditProps {
	cvData: CVDataType | null;
}

export const CVGitStats: FunctionComponent<FormEditProps> = ({ cvData }) => {
	const [gitHubData, setGitHubData] = useState<GitHubData>();
	const [loading, setLoading] = useState<boolean>(false);

	useEffect(() => {
		setLoading(true);
		fetchGitHubData(cvData?.id).then((data) => {
			setGitHubData(data);
			console.log(data);
		});
		setLoading(false);
	}, [cvData]);

	const data =
		gitHubData?.statistics.languages.languages.map((lang: GitHubLanguage) => {
			return { type: lang.language, value: lang.repo_count };
		}) || [];

	const total = data.reduce((sum, item) => sum + item.value, 0);

	const dataWithPercentage = data.map((item) => ({
		...item,
		percentage: total > 0 ? ((item.value / total) * 100).toFixed(2	) : 0,
	}));

	const config = {
		data: dataWithPercentage,
		angleField: "value",
		colorField: "type",
		innerRadius: 0.6,
		label: {
			text: (datum: any) => {
				return `${datum.data?.percentage || datum.percentage}%`;
			},
			style: {
				fontWeight: "bold",
			},
		},
		legend: {
			color: {
				title: false,
				position: "right",
				rowPadding: 5,
			},
		},
		annotations: [
			{
				type: "text",
				style: {
					text: "Top \nLanguages\n by Repo",
					x: "50%",
					y: "50%",
					textAlign: "center",
					fontSize: 20,
					fontStyle: "bold",
				},
			},
		],
	};

	return (
		<div>
			{gitHubData && (
				<div>
					<Pie loading={loading} {...config} />
				</div>
			)}
		</div>
	);
};
