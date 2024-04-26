import streamlit as st
import nltk
import spacy
import os

nltk.download('stopwords')
spacy.load('en_core_web_sm')

import base64
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course


def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


# def show_pdf(file_path):
#     with open(file_path, "rb") as f:
#         base64_pdf = base64.b64encode(f.read()).decode()
#     print(file_path)
#     pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
#     # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
#
#     st.markdown(file_path, unsafe_allow_html=True)
#     st.markdown('<iframe src="data:application/pdf;base64,{}" width="100%" height="800px" type="application/pdf"></iframe>'.format(base64_pdf), unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Kurslar & Sertifikatlar🎓 bo'yicha Tavsiyalar**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Kurs tavsiyalari sonini tanlang:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


st.set_page_config(
    page_title="Aqlli Resume Analiz qiluvchi",
    page_icon='./Logo/Logo.ico',
)

def run():
    st.title("Aqlli Resume Tahlilchisi")
    img = Image.open('Logo/Logo.jpg')
    img = img.resize((250, 250))
    st.image(img)

    pdf_file = st.file_uploader("Resume Tanlang", type=["pdf"])
    if pdf_file is not None:
        save_image_path = './Upload_Resumes/' + pdf_file.name
        # with open(save_image_path, "rb") as f:
        #     base64_pdf = base64.b64encode(f.read()).decode()

        pdf_display = f'<iframe src="{save_image_path}" width="100%" height="800px""></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        with open(save_image_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        resume_data = ResumeParser(save_image_path).get_extracted_data()
        if resume_data:
            ## Get the whole Upload_Resumes data
            resume_text = pdf_reader(save_image_path)

            st.header("**Resume Analizi:**")
            st.success("Salom " + resume_data['name'])
            st.subheader("**Sizning Asosiy ma'lumotlaringiz**")
            try:
                st.text('Ism: ' + resume_data['name'])
                st.text('Email: ' + resume_data['email'])
                st.text('Contact: ' + resume_data['mobile_number'])
                st.text('Sahifalar soni: ' + str(resume_data['no_of_pages']))
            except:
                pass
            cand_level = ''
            if resume_data['no_of_pages'] == 1:
                cand_level = "Boshlang'ich"
                st.markdown(
                    '''<h4 style='text-align: left; color: #d73b5c;'>Tahlilga ko'ra Boshlang'ich darajadasiz.</h4>''',
                    unsafe_allow_html=True)
            elif resume_data['no_of_pages'] == 2:
                cand_level = "O'rta"
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Tahlilga ko'ra O'rta darajadasiz!</h4>''',
                            unsafe_allow_html=True)
            elif resume_data['no_of_pages'] >= 3:
                cand_level = "Tajribali"
                st.markdown('''<h4 style='text-align: left; color: #fba171;'>Tahlilga ko'ra Tajribalisiz!''',
                            unsafe_allow_html=True)

            st.subheader("**Ko'nikmalar bo'yicha tavsiya💡**")
            ## Skill shows
            keywords = st_tags(label='### Sizning ko\'nikmalaringiz',
                               text='Ko\'nikmalaringiz bo\'yicha tavsiyalar',
                               value=resume_data['skills'], key='1')

            ##  recommendation
            ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                          'streamlit']
            web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                           'javascript', 'angular js', 'c#', 'flask']
            android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
            ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
            uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                            'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                            'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                            'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                            'user research', 'user experience']

            recommended_skills = []
            reco_field = ''
            rec_course = ''
            ## Courses recommendation
            for i in resume_data['skills']:
                ## Data science recommendation
                if i.lower() in ds_keyword:
                    print(i.lower())
                    reco_field = 'Data Science'
                    st.success(
                        "** Bizning tahlilimiz shuni ko'rsatadiki, siz Data Science bo'yicha ishlarni qidiryapsiz **")
                    recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                          'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                          'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                          'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                          'Streamlit']
                    recommended_keywords = st_tags(label='### Ko\'nikmalaringiz bo\'yicha tavsiyalar.',
                                                   text='Tizimdan tavsiyalar',
                                                   value=recommended_skills, key='2')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Rezyume uchun ushbu ko'nikmalarni qo'shish 🚀 ishga joylashish imkoniyatini oshiradi💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(ds_course)
                    break

                ## Web development recommendation
                elif i.lower() in web_keyword:
                    print(i.lower())
                    reco_field = 'Web Development'
                    st.success(
                        "** Bizning tahlilimiz shuni ko'rsatadiki, siz Web Development bo'yicha ishlarni qidiryapsiz **")
                    recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                          'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                   text='Tizimdan tavsiyalar',
                                                   value=recommended_skills, key='3')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Rezyume uchun ushbu ko'nikmalarni qo'shish 🚀 ishga joylashish imkoniyatini oshiradi💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(web_course)
                    break

                ## Android App Development
                elif i.lower() in android_keyword:
                    print(i.lower())
                    reco_field = 'Android Development'
                    st.success(
                        "** Bizning tahlilimiz shuni ko'rsatadiki, siz Android App Development bo'yicha ishlarni qidiryapsiz **")
                    recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                          'Kivy', 'GIT', 'SDK', 'SQLite']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                   text='Tizimdan tavsiyalar',
                                                   value=recommended_skills, key='4')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Rezyume uchun ushbu ko'nikmalarni qo'shish 🚀 ishga joylashish imkoniyatini oshiradi💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(android_course)
                    break

                ## IOS App Development
                elif i.lower() in ios_keyword:
                    print(i.lower())
                    reco_field = 'IOS Development'
                    st.success(
                        "** Bizning tahlilimiz shuni ko'rsatadiki, siz IOS App Development bo'yicha ishlarni qidiryapsiz **")
                    recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                          'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                          'Auto-Layout']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                   text='Tizimdan tavsiyalar',
                                                   value=recommended_skills, key='5')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Rezyume uchun ushbu ko'nikmalarni qo'shish 🚀 ishga joylashish imkoniyatini oshiradi💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(ios_course)
                    break

                ## Ui-UX Recommendation
                elif i.lower() in uiux_keyword:
                    print(i.lower())
                    reco_field = 'UI-UX Development'
                    st.success(
                        "** Bizning tahlilimiz shuni ko'rsatadiki, siz UI-UX Development bo'yicha ishlarni qidiryapsiz **")
                    recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                          'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                          'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                          'Solid', 'Grasp', 'User Research']
                    recommended_keywords = st_tags(label='### Siz uchun tavsiya qilinadigan ko\'nikmalar.',
                                                   text='Tizimdan tavsiyalar',
                                                   value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Rezyume uchun ushbu ko'nikmalarni qo'shish 🚀 ishga joylashish imkoniyatini oshiradi💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(uiux_course)
                    break

            #
            ## Insert into table
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date + '_' + cur_time)

            ### Resume writing recommendation
            st.subheader("**Maslahatlar va g'oyalar💡**")
            resume_score = 0
            if 'Objective' in resume_text:
                resume_score = resume_score + 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Ajoyib! Maqsad qo'shgansiz</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] Bizning tavsiyamizga ko'ra, iltimos, o'z martaba maqsadingizni qo'shing, bu sizning martaba niyyatingizni Ishga qabul qiluvchilarga beradi.</h4>''',
                    unsafe_allow_html=True)

            if 'Declaration' in resume_text:
                resume_score = resume_score + 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Ajoyib! Siz Delkaratsiyani qo'shdingiz✍/h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] Bizning tavsiyamizga ko'ra, Deklaratsiya✍ qo'shing. Bu sizning rezyumeingizda yozilgan hamma narsa to'g'ri ekanligiga va siz tomonidan to'liq tan olinganligiga ishonch hosil qiladi.</h4>''',
                    unsafe_allow_html=True)

            if 'Hobbies' or 'Interests' in resume_text:
                resume_score = resume_score + 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Ajoyib! Siz sevimli mashg'ulotlaringizni⚽ qo'shdingiz</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] Tavsiyamizga ko'ra, iltimos, Xobbi⚽ qo'shing. Bu yollovchilarga sizning shaxsiyatingizni ko'rsatadi va bu o'ringa mos yoki mos emasligingizga ishonch hosil qilishadi.</h4>''',
                    unsafe_allow_html=True)

            if 'Achievements' in resume_text:
                resume_score = resume_score + 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Ajoyib! Siz o'z yutuqlaringizni qo'shdingiz🏅 </h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] Tavsiyamizga ko'ra, Yutuqlar qo'shing🏅. Bu sizga kerakli lavozimga qodir ekanligingizni ko'rsatadi.</h4>''',
                    unsafe_allow_html=True)

            if 'Projects' in resume_text:
                resume_score = resume_score + 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Ajoyib! Loyihalaringizni qo'shdingiz👨‍💻 </h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] Bizning tavsiyamizga ko'ra, loyihalarni qo'shing👨‍💻. Bu sizga kerakli lavozim bilan bog'liq ish qilganingizni yoki yo'qligini ko'rsatadi.</h4>''',
                    unsafe_allow_html=True)

            st.subheader("**Rezyume balli📝**")
            st.markdown(
                """
                <style>
                    .stProgress > div > div > div > div {
                        background-color: #d73b5c;
                    }
                </style>""",
                unsafe_allow_html=True,
            )
            my_bar = st.progress(0)
            score = 0
            for percent_complete in range(resume_score):
                score += 1
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1)
            st.success('** Sizning rezyumeni yozish ballingiz: ' + str(score) + '**')
            st.warning(
                "** Note: Ushbu ball rezyumeingizga qo'shgan kontentingiz asosida hisoblanadi. **")
            st.balloons()
        else:
            st.error('Nimadir xato..')

run()
