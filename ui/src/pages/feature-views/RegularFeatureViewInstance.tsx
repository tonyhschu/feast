import React from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import {
  EuiPageHeader,
  EuiPageContent,
  EuiPageContentBody,
} from "@elastic/eui";

import { FeatureViewIcon32 } from "../../graphics/FeatureViewIcon";
import { enabledFeatureStatistics } from "../,,/../../flags";

import { useMatchExact, useMatchSubpath } from "../../hooks/useMatchSubpath";
import { FeastFeatureViewType } from "../../parsers/feastFeatureViews";
import RegularFeatureViewOverviewTab from "./RegularFeatureViewOverviewTab";
import FeatureViewSummaryStatisticsTab from "./FeatureViewSummaryStatisticsTab";

import {
  useRegularFeatureViewCustomTabs,
  useRegularFeatureViewCustomTabRoutes,
} from "../../custom-tabs/TabsRegistryContext";

interface RegularFeatureInstanceProps {
  data: FeastFeatureViewType;
}

const RegularFeatureInstance = ({ data }: RegularFeatureInstanceProps) => {
  const navigate = useNavigate();

  const { customNavigationTabs } = useRegularFeatureViewCustomTabs(navigate);
  let tabs = [
    {
      label: "Overview",
      isSelected: useMatchExact(""),
      onClick: () => {
        navigate("");
      },
    },
  ];

  let statisticsIsSelected = useMatchSubpath("statistics");
  if (enabledFeatureStatistics) {
    tabs.push({
      label: "Statistics",
      isSelected: statisticsIsSelected,
      onClick: () => {
        navigate("statistics");
      },
    });
  }

  tabs.push(...customNavigationTabs);

  const TabRoutes = useRegularFeatureViewCustomTabRoutes();

  return (
    <React.Fragment>
      <EuiPageHeader
        restrictWidth
        iconType={FeatureViewIcon32}
        pageTitle={`${data.spec.name}`}
        tabs={tabs}
      />
      <EuiPageContent
        hasBorder={false}
        hasShadow={false}
        paddingSize="none"
        color="transparent"
        borderRadius="none"
      >
        <EuiPageContentBody>
          <Routes>
            <Route
              path="/"
              element={<RegularFeatureViewOverviewTab data={data} />}
            />
            <Route
              path="/statistics"
              element={<FeatureViewSummaryStatisticsTab />}
            />
            {TabRoutes}
          </Routes>
        </EuiPageContentBody>
      </EuiPageContent>
    </React.Fragment>
  );
};

export default RegularFeatureInstance;
