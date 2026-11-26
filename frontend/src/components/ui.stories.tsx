import type { Meta, StoryObj } from "@storybook/react-vite";
import { Button, Card, Badge, Progress, Empty, PageHeading } from "./ui";
const meta = { title: "NIKWAY/Patterns", component: Card } satisfies Meta<
  typeof Card
>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Actions: Story = {
  render: () => (
    <Card>
      <PageHeading
        title="اقدام روشن، انتخاب ساده"
        description="نمونه سیستم طراحی — داده یادگیری نیست"
      />
      <div className="actions">
        <Button>ادامه یادگیری</Button>
        <Button variant="outline">مشاهده دوره</Button>
        <Button variant="ghost">بازگشت</Button>
        <Button disabled>در انتظار اتصال</Button>
      </div>
    </Card>
  ),
};
export const Feedback: Story = {
  render: () => (
    <Card>
      <h2>حالت‌ها و پیشرفت</h2>
      <div className="actions">
        <Badge tone="success">ثبت شد</Badge>
        <Badge tone="warning">متصل نشده</Badge>
        <Badge>دوره آموزشی</Badge>
      </div>
      <Progress label="پیشرفت نمونه" value={45} />
      <p className="error-banner">دریافت اطلاعات ممکن نشد. دوباره تلاش کنید.</p>
    </Card>
  ),
};
export const EmptyState: Story = {
  render: () => (
    <Empty
      title="دوره‌ای پیدا نشد"
      action={<Button variant="outline">حذف فیلتر</Button>}
    >
      عبارت جست‌وجو را تغییر دهید.
    </Empty>
  ),
};
export const Form: Story = {
  render: () => (
    <Card>
      <h2>پاسخ تمرین</h2>
      <label htmlFor="story-answer">متن پاسخ و شواهد</label>
      <textarea id="story-answer" aria-describedby="help" />
      <p id="help" className="muted">
        برای بازبینی انسانی ارسال می‌شود.
      </p>
      <Button>ارسال برای بازبینی</Button>
    </Card>
  ),
};
